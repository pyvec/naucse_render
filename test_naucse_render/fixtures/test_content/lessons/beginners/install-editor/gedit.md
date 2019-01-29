{% set editor_name = 'Gedit' %}
{% set editor_cmd = 'gedit' %}
{% set editor_url = 'https://wiki.gnome.org/Apps/Gedit' %}
{% extends lesson.slug + '/_linux_base.md' %}

{% block name_gen %} Geditu {% endblock %}


{% block setup %}

...

Číslování řádků
:   V sekci Zobrazit/<span class="en">View</span> vyber
    Zobrazovat čísla řádků/<span class="en">Display Line Numbers</span>.

    {{ figure(img=static('gedit_linenums.png'), alt="") }}

...

{% endblock %}
