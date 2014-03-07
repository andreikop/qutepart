all:
	gcc \
		-g \
		-Wall \
		mp.c \
		-lavformat -lavcodec -lavutil \
		-lrt \
		-o mp

run:
	./mp
