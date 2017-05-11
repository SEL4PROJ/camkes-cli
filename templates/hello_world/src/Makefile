TARGETS := $(notdir ${SOURCE_DIR}).cdl
ADL := {{ name }}.camkes

HelloWorld_CFILES := $(patsubst ${SOURCE_DIR}/%,%,$(wildcard ${SOURCE_DIR}/components/HelloWorld/src/*.c))
HelloWorld_HFILES := $(patsubst ${SOURCE_DIR}/%,%,$(wildcard ${SOURCE_DIR}/components/HelloWorld/include/*.h))

include ${PWD}/tools/camkes/camkes.mk
