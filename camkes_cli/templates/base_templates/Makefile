TARGETS := $(notdir ${SOURCE_DIR}).cdl
ADL := {{ name }}.camkes

COMPONENT_DIRS = components
COMPONENTS := $(foreach COMPONENT_DIR, ${COMPONENT_DIRS}, $(patsubst ${SOURCE_DIR}/${COMPONENT_DIR}/%,%,$(wildcard ${SOURCE_DIR}/${COMPONENT_DIR}/*)))

# create the appropriate build system variables for building components
$(foreach COMPONENT,${COMPONENTS},$(eval ${COMPONENT}_CFILES := $(patsubst ${SOURCE_DIR}/%,%,$(wildcard $(foreach COMPONENT_DIR,${COMPONENT_DIRS},${SOURCE_DIR}/${COMPONENT_DIR}/${COMPONENT}/src/*.c)))))
$(foreach COMPONENT,${COMPONENTS},$(eval ${COMPONENT}_HFILES := $(patsubst ${SOURCE_DIR}/%,%,$(wildcard $(foreach COMPONENT_DIR,${COMPONENT_DIRS},${SOURCE_DIR}/${COMPONENT_DIR}/${COMPONENT}/include/*.h)))))

include ${PWD}/tools/camkes/camkes.mk
