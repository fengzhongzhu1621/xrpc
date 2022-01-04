from x_rpc.utils.choices import ChoicesEnum, ChoicesValue


class ExampleChoicesEnum(ChoicesEnum):
    A = 1
    B = 2

    _members = (ChoicesValue(id=A, name="labelA"), ChoicesValue(id=B, name="labelB"))


class TestChoices:
    def test_get_choices(self):
        actual = ExampleChoicesEnum.get_choices()
        expect = ((1, 'labelA'), (2, 'labelB'))
        assert actual == expect

    def test_get_dict_choices(self):
        actual = ExampleChoicesEnum.get_dict_choices()
        expect = {1: 'labelA', 2: 'labelB'}
        assert actual == expect

    def test_get_choices_drop_down_list(self):
        actual = ExampleChoicesEnum.get_choices_drop_down_list()
        expect = [{'id': 1, 'name': 'labelA'}, {'id': 2, 'name': 'labelB'}]
        assert actual == expect
