"""
Example of using Cocotb to send image files in to the opencores JPEG Encoder
and check that the output is sufficiently similar to the input.

NB Limited to 96x96 images since we're using a static JPEG header.
"""
import os
import io
import logging
from itertools import izip
from PIL import Image

import cocotb
from cocotb.result import TestFailure
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly

from cocotb.drivers import Driver
from cocotb.monitors import Monitor
from cocotb.regression import TestFactory

_jpeg_header = open("header.bin", "r").read()

class JpegMonitor(Monitor):

    def __init__(self, dut, **kwargs):
        self.dut = dut
        Monitor.__init__(self, **kwargs)

    @cocotb.coroutine
    def _monitor_recv(self):
        """Creates an Image object from the output of the DUT"""
        data = ""

        clkedge = RisingEdge(self.dut.clk)
        ro = ReadOnly()
        while True:
            yield clkedge
            yield ro
            if self.dut.data_ready.value:
                data += self.dut.JPEG_bitstream.value.buff
            if self.dut.eof_data_partial_ready.value:
                f_obj = io.BytesIO(_jpeg_header + data + "\xff\xd9")
                img = Image.open(f_obj)
                self.log.info("Recovered image %s of %dx%d in mode %s" % (
                    img.format, img.size[0], img.size[1], img.mode))
                yield clkedge
                self._recv(img)
                data = ""


class ImageDriver(Driver):

    def __init__(self, dut):
        self.dut = dut
        Driver.__init__(self)

    @cocotb.coroutine
    def _driver_send(self, image, **kwargs):
        """
        Send an image into the DUT.  Image should be in RGB format and a 
        multiple of 8 pixels in both width and height

        Args:

            image (PIL.Image)   image to send into the dut
        """
        if image.mode != "RGB":
            raise TypeError("Require an format RGB image")

        width, height = image.size
        dut = self.dut                         # Local reference to save lookup
        clk_edge = RisingEdge(dut.clk)         # Recycle objects for efficiency

        yield clk_edge                         # Reset the dut first
        dut.rst <= 1
        yield clk_edge
        dut.rst <= 0
        dut.end_of_file_signal <= 0

        pixels = image.load()

        for y in xrange(0,height,8):
            for x in xrange(0,width,8):
                dut.enable <= 1

                self.log.debug("Sending block X% 4d/% 4d, Y% 4d/% 4d" % (
                        x, width, y, height))

                if y >= height-8 and x >= width-8:
                    dut.end_of_file_signal <= 1

                for y_block in xrange(8):
                    for x_block in xrange(8):
                        # If the image isn't a multiple of 8 pixels we 
                        # repeat the edge values (see Readme.doc)
                        x_ofs = min(x+x_block, width-1)
                        y_ofs = min(y+y_block, height-1)

                        r,g,b = pixels[x_ofs, y_ofs]
                        dut.data_in <= (b<<16 | g<<8 | r)
                        yield clk_edge
                        dut.end_of_file_signal <= 0

                for i in xrange(33):
                    yield clk_edge

                dut.enable <= 0
                yield clk_edge


def compare(i1, i2):
    """
    Compare the similarity of two images

    From http://rosettacode.org/wiki/Percentage_difference_between_images
    """
    assert i1.mode == i2.mode, "Different kinds of images."
    assert i1.size == i2.size, "Different sizes."

    pairs = izip(i1.getdata(), i2.getdata())
    dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
    ncomponents = i1.size[0] * i1.size[1] * 3
    return (dif / 255.0 * 100) / ncomponents


@cocotb.coroutine
def process_image(dut, filename="", debug=False, threshold=0.22):
    """Run an image file through the jpeg encoder and compare the result"""

    cocotb.fork(Clock(dut.clk, 100).start())

    driver = ImageDriver(dut)
    monitor = JpegMonitor(dut)

    if debug:
        driver.log.setLevel(logging.DEBUG)
        monitor.log.setLevel(logging.DEBUG)

    stimulus = Image.open(filename)
    yield driver.send(stimulus)
    output = yield monitor.wait_for_recv()

    if debug:
        output.save(filename + "_process.jpg")

    difference = compare(stimulus, output)

    dut.log.info("Compressed image differs to original by %f%%" % (difference))

    if difference > threshold:
        raise TestFailure("Resulting image file was too different (%f > %f)" %
                          (difference, threshold))


tf = TestFactory(process_image)
tf.add_option("filename", [os.path.join('test_images', f)
                            for f in os.listdir('test_images')])
tf.generate_tests()
