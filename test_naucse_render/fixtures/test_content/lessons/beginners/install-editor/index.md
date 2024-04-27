...


## Co programátorský editor umí

...

Podpora více souborů
:   Větší projekty sestávají z více souborů, které můžeš mít v editoru
    otevřené všechny najednou.

Číslování řádků
:   Před každým řádkem se ukazuje číslo.
    To se bude velice hodit, až Python bude nadávat, že chyba je na řádku 183. 

...

> [note]
>
> Pro ilustraci, takhle může v editoru vypadat kousek kódu:
>
> ```python
>     1  @app.route('/courses/<course:course>/')
>     2  def course_page(course):
>     3      ...
> ```


## Volba a nastavení editoru

...

* [Atom]({{ subpage_url('atom') }}) – doporučený editor pro
  Windows a macOS.

...

* [Gedit]({{ subpage_url('gedit') }}) – bývá na systémech s prostředím GNOME.
  * Můžeme odkázat na [Nácvik odsazování]({{ subpage_url('gedit') }}#nacvik_odsazovani).

...

{% filter solution %}
```python
# Třikrát:
for i in range(3):

    # Nakresli čtverec (kód zkopírovaný z předchozí úlohy a odsazený)
    for j in range(4):
        forward(50)
        left(90)

    # Otoč se o 20°
    left(20)

```
{% endfilter %}
