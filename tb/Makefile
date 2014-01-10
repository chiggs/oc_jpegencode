TOPLEVEL=jpeg_top
MODULE=test_jpeg_top

PWD=$(shell pwd)
VERILOG_SOURCES = $(PWD)/../code/y_huff.v \
                  $(PWD)/../code/y_quantizer.v \
                  $(PWD)/../code/y_dct.v \
                  $(PWD)/../code/cb_huff.v \
                  $(PWD)/../code/cb_quantizer.v \
                  $(PWD)/../code/cb_dct.v \
                  $(PWD)/../code/cr_huff.v \
                  $(PWD)/../code/cr_quantizer.v \
                  $(PWD)/../code/cr_dct.v \
                  $(PWD)/../code/yd_q_h.v \
                  $(PWD)/../code/cbd_q_h.v \
                  $(PWD)/../code/crd_q_h.v \
                  $(PWD)/../code/rgb2ycbcr.v \
                  $(PWD)/../code/sync_fifo_ff.v \
                  $(PWD)/../code/sync_fifo_32.v \
                  $(PWD)/../code/pre_fifo.v \
                  $(PWD)/../code/ff_checker.v \
                  $(PWD)/../code/fifo_out.v \
                  $(PWD)/../code/jpeg_top.v

include $(COCOTB)/makefiles/Makefile.inc
include $(COCOTB)/makefiles/Makefile.sim

clean::
	-@rm -f *.pyc
	-@rm -f *.jpg
	-@rm -f results.xml
