
.PHONY: all sim clean

all: sim

sim_build:
	mkdir -p sim_build

sim_build/sim.vvp: sim_build
	iverilog -s jpeg_top_tb -o sim_build/sim.vvp /home/chiggs/code/jpegencode/tb/../code/y_huff.v /home/chiggs/code/jpegencode/tb/../code/y_quantizer.v /home/chiggs/code/jpegencode/tb/../code/y_dct.v /home/chiggs/code/jpegencode/tb/../code/cb_huff.v /home/chiggs/code/jpegencode/tb/../code/cb_quantizer.v /home/chiggs/code/jpegencode/tb/../code/cb_dct.v /home/chiggs/code/jpegencode/tb/../code/cr_huff.v /home/chiggs/code/jpegencode/tb/../code/cr_quantizer.v /home/chiggs/code/jpegencode/tb/../code/cr_dct.v /home/chiggs/code/jpegencode/tb/../code/yd_q_h.v /home/chiggs/code/jpegencode/tb/../code/cbd_q_h.v /home/chiggs/code/jpegencode/tb/../code/crd_q_h.v /home/chiggs/code/jpegencode/tb/../code/rgb2ycbcr.v /home/chiggs/code/jpegencode/tb/../code/sync_fifo_ff.v /home/chiggs/code/jpegencode/tb/../code/sync_fifo_32.v /home/chiggs/code/jpegencode/tb/../code/pre_fifo.v /home/chiggs/code/jpegencode/tb/../code/ff_checker.v /home/chiggs/code/jpegencode/tb/../code/fifo_out.v /home/chiggs/code/jpegencode/tb/../code/jpeg_top.v /home/chiggs/code/jpegencode/tb/../code/jpeg_top_TB.v

sim: sim_build/sim.vvp
	cd sim_build && vvp sim.vvp

clean:
	-rm -rf sim_build
