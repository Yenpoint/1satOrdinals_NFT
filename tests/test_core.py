import pytest
from pathlib import Path
from bsv.script import Script, P2PKH
from yenpoint_1satordinals.core import OneSatOrdinal, read_file_and_get_mime_type, add_1sat_outputs

class TestOneSatOrdinal:
    def test_create_inscription(self):
        # テストデータ
        content_type = "text/plain"
        data = "Hello, Ordinals!"
        
        # インスクリプションの作成
        inscription = OneSatOrdinal.create_inscription(content_type, data)
        
        # 戻り値がScriptインスタンスであることを確認
        assert isinstance(inscription, Script)
        # スクリプトにordが含まれていることを確認
        assert b'ord' in inscription.serialize()
        # content_typeが含まれていることを確認
        assert content_type.encode() in inscription.serialize()
        # データが含まれていることを確認
        assert data.encode() in inscription.serialize()

    def test_create_1sat_ordinal(self):
        # テストデータ
        ordinal_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # サンプルアドレス
        content_type = "text/plain"
        data = "Hello, Ordinals!"
        
        # 1Sat Ordinalスクリプトの作成
        ordinal_script = OneSatOrdinal.create_1sat_ordinal(ordinal_address, content_type, data)
        
        # 戻り値がScriptインスタンスであることを確認
        assert isinstance(ordinal_script, Script)
        # P2PKHスクリプトが含まれていることを確認
        p2pkh_script = P2PKH().lock(ordinal_address)
        assert p2pkh_script.serialize() in ordinal_script.serialize()

def test_read_file_and_get_mime_type(tmp_path):
    # テスト用の一時ファイルを作成
    test_file = tmp_path / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)
    
    # ファイル読み込みとMIMEタイプの取得をテスト
    data, mime_type = read_file_and_get_mime_type(test_file)
    
    assert data == test_content.encode()
    assert mime_type == "text/plain"

def test_add_1sat_outputs():
    # テストデータ
    ordinal_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    change_address = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"
    test_data = "Hello, Ordinals!"
    
    # 1satの出力を作成
    outputs = add_1sat_outputs(ordinal_address, test_data, change_address)
    
    # 出力が3つ（NFT、手数料、おつり）あることを確��
    assert len(outputs) == 3
    
    # NFT出力の検証
    nft_output = outputs[0]
    assert nft_output.satoshis == 1
    assert not nft_output.change
    
    # 手数料出力の検証
    fee_output = outputs[1]
    assert fee_output.satoshis == OneSatOrdinal.FEE_AMOUNT
    assert not fee_output.change
    # P2PKHスクリプトとして比較
    expected_script = P2PKH().lock(OneSatOrdinal.YENPOINT_ADDRESS)
    assert str(fee_output.locking_script) == str(expected_script)
    
    # おつり出力の検証
    change_output = outputs[2]
    assert change_output.change
    # P2PKHスクリプトとして比較
    expected_change_script = P2PKH().lock(change_address)
    assert str(change_output.locking_script) == str(expected_change_script)

def test_file_not_found():
    # 存在しないファイルパスでのテスト
    with pytest.raises(FileNotFoundError):
        read_file_and_get_mime_type(Path("nonexistent_file.txt"))

def test_invalid_mime_type(tmp_path):
    # 無効な拡張子のファイルでのテスト
    test_file = tmp_path / "test.invalidext"
    test_file.write_text("test content")
    
    with pytest.raises(ValueError):
        read_file_and_get_mime_type(test_file) 