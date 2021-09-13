from naucse_render.compile import unique_path

def test_unique_path(tmp_path):
    path = tmp_path / 'file.ext'
    paths = set()
    for i in range(10):
        assert len(paths) == i
        paths.add(path)
        path.write_text(str(i))
        path = unique_path(path)
        assert tmp_path in path.parents
