ARD = arduino-cli
CC = $(ARD) compile
UC = $(ARD) upload
PORT = /dev/ttyACM0
CFLAGS = --fqbn arduino:avr:mega
UFLAGS = -p $(PORT) $(CFLAGS)
SRC = tada_firmware


all: compile upload

compile: ./$(SRC)/$(SRC).ino
	$(CC) $(CFLAGS) $(SRC)

upload:
	$(UC) $(UFLAGS) $(SRC)

clean:
	rm -f ./$(SRC)/*.hex
	rm -f ./$(SRC)/*.elf
	rm -rf ./$(SRC)/build
