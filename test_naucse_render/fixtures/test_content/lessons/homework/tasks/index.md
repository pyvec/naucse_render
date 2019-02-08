<ol>
{% for item in data.tasks %}
    <li>
        {{ item.markdown | markdown }}
    </li>
{% endfor %}
</ol>
