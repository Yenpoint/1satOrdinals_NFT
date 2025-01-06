import asyncio
from pathlib import Path

from yenpoint_1satordinals import add_1sat_outputs

from bsv.transaction_input import TransactionInput
from bsv.transaction_output import TransactionOutput
from bsv.transaction import Transaction
from bsv import PrivateKey
from bsv.script import P2PKH


# from here the test of the code

async def main():
    try:

        # To set the file path to the data for your NFT.
        data_path = Path("data/image1.png")
        outputs = add_1sat_outputs(
            ordinal_address="1AXBtEUcKpmFSTPE8TK85LkE96N2uMcDuK",
            data=data_path,
            change_address="17wxeSxYyUrtygrsNiK5tGTcoxksBRMU3Y"
        )

        # Previous transaction details
        previous_tx_vout = 1
        previous_tx_file_path = "data/tx1.txt"

        # Read the previous transaction
        with open(previous_tx_file_path, 'r') as f:
            previous_tx_rawtx = f.read()

        previous_tx = Transaction.from_hex(previous_tx_rawtx)
        # Set up keys and addresses
        # Sender details
        sender_private_key = PrivateKey("L1X1sP2CvK-----ur5LQHeJWDoW")

        tx_input = TransactionInput(
            source_transaction=previous_tx,
            source_txid=previous_tx.txid(),
            source_output_index=previous_tx_vout,
            unlocking_script_template=P2PKH().unlock(sender_private_key)
        )
        # #  もしアウトプットを追加したい場合
        # Additional_output = TransactionOutput(
        #     locking_script=P2PKH().lock("1QnWY1CWbWGeqobBBoxdZZ3DDeWUC2VLn"),
        #     satoshis=33,
        #     change=False
        # )
        #
        # tx = Transaction([tx_input], outputs + [Additional_output])
        tx = Transaction([tx_input], outputs)
        tx.fee()
        tx.sign()
        thetxid = tx.txid()
        txhex = tx.hex()
        print(thetxid)
        print(txhex)
        # await tx.broadcast()

    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
