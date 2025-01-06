import mimetypes
from typing import Union, List, Tuple
from pathlib import Path

from bsv.constants import OpCode
from bsv.utils import encode_pushdata
from bsv.transaction_output import TransactionOutput
from bsv.script import P2PKH, Script


class OneSatOrdinal:
    """
    1Sat Ordinalsの作成と管理を行うクラス
    BSVブロックチェーン上のNFTの特殊な形式を扱います
    """

    YENPOINT_ADDRESS = "1CBTMTqXZZ8VLNNZ4Vxrdj2hzvaLUWMLwt"  # Yenpointの手数料受取アドレス
    FEE_AMOUNT = 998  # satoshis単位での手数料額

    @classmethod
    def create_inscription(cls, content_type: str, data: Union[str, bytes]) -> Script:
        """
        Ordinal用のinscriptionスクリプトを作成します

        Args:
            content_type (str): データのMIMEタイプ
            data (Union[str, bytes]): インスクリプションに含めるデータ

        Returns:
            Script: 作成されたインスクリプションスクリプト
        """
        ord_varint = encode_pushdata("ord".encode())
        content_type_varint = encode_pushdata(content_type.encode())
        data_bytes = data if isinstance(data, bytes) else data.encode('utf-8')
        data_varint = encode_pushdata(data_bytes)

        return Script(
            OpCode.OP_FALSE + OpCode.OP_IF +
            ord_varint + OpCode.OP_1 + content_type_varint +
            OpCode.OP_0 + data_varint + OpCode.OP_ENDIF
        )

    @classmethod
    def create_1sat_ordinal(cls, ordinal_address: str, content_type: str, data: Union[str, bytes]) -> Script:
        """
        インスクリプションとP2PKHロッキングスクリプトを組み合わせた完全な1Sat Ordinalスクリプトを作成します

        Args:
            ordinal_address (str): Ordinalの送信先アドレス
            content_type (str): データのMIMEタイプ
            data (Union[str, bytes]): インスクリプションに含めるデータ

        Returns:
            Script: 作成された1Sat Ordinalスクリプト
        """
        inscription = cls.create_inscription(content_type, data)
        locking_script = P2PKH().lock(ordinal_address)
        return Script(locking_script.serialize() + inscription.serialize())


def read_file_and_get_mime_type(file_path: Union[str, Path]) -> Tuple[bytes, str]:
    """
    ファイルを読み込み、そのMIMEタイプを検出します

    Args:
        file_path (Union[str, Path]): 読み込むファイルのパス

    Returns:
        Tuple[bytes, str]: (ファイルのバイナリデータ, MIMEタイプ)の形式のタプル

    Raises:
        FileNotFoundError: 指定されたファイルが存在しない場合
        ValueError: MIMEタイプが検出できない場合
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'rb') as file:
        data = file.read()

    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        raise ValueError(f"Could not determine MIME type for file: {file_path}")

    return data, content_type


class OrdinalOutputs():
    """
        1Sat OrdinalのNFT出力と手数料出力をまとめて扱うためのクラス
        リストの中で自動的に展開される
        """

    def __init__(self, nft_output: TransactionOutput, fee_output: TransactionOutput, change_output: TransactionOutput):
        self.nft_output = nft_output
        self.fee_output = fee_output
        self.change_output = change_output

        self._outputs = [nft_output, fee_output]

    def __repr__(self):
        return f"OrdinalOutputs({len(self._outputs)} outputs)"

    def __iter__(self):
        """リストとして展開される際に呼ばれる"""
        return iter(self._outputs)

    def __add__(self, other):
        """+ 演算子での連結をサポート"""
        if isinstance(other, (list, OrdinalOutputs)):
            return self._outputs + list(other)
        return NotImplemented

    def __radd__(self, other):
        """+ 演算子での右からの連結をサポート"""
        if isinstance(other, (list, OrdinalOutputs)):
            return list(other) + self._outputs
        return NotImplemented

    def get_outputs(self):
        """NFT出力と手数料出力のタプルを返す"""
        return [self.nft_output, self.fee_output, self.change_output]


def add_1sat_outputs(ordinal_address: str, data: Union[str, Path], change_address: str) -> OrdinalOutputs:
    try:
        # データの処理
        if isinstance(data, Path):
            file_data, content_type = read_file_and_get_mime_type(data)

        else:
            # 文字列の場合
            file_data = str(data).encode('utf-8')
            content_type = 'text/plain'

        # 1sat出力の作成
        ordinal_script = OneSatOrdinal.create_1sat_ordinal(ordinal_address, content_type, file_data)
        sat_output = TransactionOutput(
            locking_script=ordinal_script,
            satoshis=1,
            change=False
        )

        # Yenpoint手数料出力の作成
        fee_output = TransactionOutput(
            locking_script=P2PKH().lock(OneSatOrdinal.YENPOINT_ADDRESS),
            satoshis=OneSatOrdinal.FEE_AMOUNT,
            change=False
        )

        change_output = TransactionOutput(
            locking_script=P2PKH().lock(change_address),
            change=True
        )

        ordinal = OrdinalOutputs(sat_output, fee_output, change_output)
        outputs = ordinal.get_outputs()
        return outputs

    except Exception as e:
        raise ValueError(f"Error creating 1sat outputs: {str(e)}")
