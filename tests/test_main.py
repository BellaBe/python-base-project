from src.main import main


def test_main(capfd):
    main()
    out, err = capfd.readouterr()
    if err:
        print(err)
    assert out == "Hello, world!\nTest\n"
