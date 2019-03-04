def test_import_shmistogram():
    import shmistogram as shm
    assert '__version__' in dir(shm)
