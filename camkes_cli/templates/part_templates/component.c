#include <camkes.h>

{% if control %}int run(void) {
    // TODO
}
{% endif %}{% for interface in interfaces %}{% for method in interface.ast.methods %}
{{ return_type(method) }} {{interface.name}}_{{ method.name }}({{ param_string(method) }}) {
    // TODO{{ default_return(method) }}
}
{% endfor %}{% endfor %}
