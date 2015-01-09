"""
Example of using Cocotb to send image files in to the opencores JPEG Encoder
and check that the output is sufficiently similar to the input.

NB Limited to 96x96 images since we're using a static JPEG header.
"""
import os

import logging
from itertools import izip
from PIL import Image

import cocotb
from cocotb.result import TestFailure
from cocotb.regression import TestFactory
from cocotb.clock import Clock

from interfaces import ImageDriver, JpegMonitor

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

    if debug:                                            # pragma: no cover
        driver.log.setLevel(logging.DEBUG)
        monitor.log.setLevel(logging.DEBUG)

    stimulus = Image.open(filename)
    yield driver.send(stimulus)
    output = yield monitor.wait_for_recv()

    if debug:                                            # pragma: no cover
        output.save(filename + "_process.jpg")

    difference = compare(stimulus, output)

    dut.log.info("Compressed image differs to original by %f%%" % (difference))

    if difference > threshold:                           # pragma: no cover
        raise TestFailure("Resulting image file was too different (%f > %f)" %
                          (difference, threshold))

tf = TestFactory(process_image)
tf.add_option("filename", [os.path.join('test_images', f)
                            for f in os.listdir('test_images')])
tf.generate_tests()
