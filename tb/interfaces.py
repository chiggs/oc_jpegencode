"""
A driver and monitor to abstract the interface to the JPEG encoder
"""

import io
from PIL import Image

import cocotb
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.drivers import Driver
from cocotb.monitors import Monitor

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
        if image.mode != "RGB":                # pragma: no cover
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

