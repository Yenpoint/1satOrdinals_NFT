# Yenpoint 1Sat Ordinals

A Python library for creating 1Sat Ordinals NFTs on the BSV blockchain.

## Installation

```bash
pip install yenpoint_1satordinals
```

## Usage

1. Preparing Ordinal NFT outputs

Use the add_1sat_outputs function.
You need three arguments, ordinal address, data, and change address.

    ordinal_address: the destination address of inscribing 1 sat ordinal NFT

    data: it can take text strings or your file path to the data that you want to inscribe.

    change_address: the address to recieve your change ammount


An example of Inscribing texts
```python
from yenpoint_1satordinals import add_1sat_outputs
from pathlib import Path


outputs = add_1sat_outputs(
    ordinal_address="your_ordinal_address",
    data="Hello, World!",
    change_address="your_change_address"
)
```
or 

An example of Inscribing data
You should define the path to the file that you want to inscribe first
```python
from yenpoint_1satordinals import add_1sat_outputs

data_path = Path("data/image1.jpeg")

outputs = add_1sat_outputs(
                    ordinal_address="1HZqesnTJK8HK4Uypvvt7FgHoBdosBvTiS",
                    data=data_path,
                    change_address="1MWLhxkoucmstD5VGLZeiaq5YMdDRMn9oS"
            )
```

Preparing the Transaction

```python
    
    from bsv.transaction_input import TransactionInput
    from bsv.transaction import Transaction
    from bsv import PrivateKey
    from bsv.script import P2PKH

        
    # Here adding the code of creating ordinal outputs
    
    
    
    tx_input = TransactionInput(
                    source_transaction=previous_tx,
                    source_txid=previous_tx.txid(),
                    source_output_index=previous_tx_vout,
                    unlocking_script_template=P2PKH().unlock(sender_private_key)
                )

    
    tx = Transaction([tx_input], outputs)

    tx.fee()
    tx.sign()
   
```



Example of customising the Transaction, adding an additional output

```python
    from bsv.transaction_input import TransactionInput
    from bsv.transaction_output import TransactionOutput
    from bsv.transaction import Transaction
    from bsv import PrivateKey
    from bsv.script import P2PKH
    
    
        # Here adding the code of creating ordinal outputs


    tx_input = TransactionInput(
                    source_transaction=previous_tx,
                    source_txid=previous_tx.txid(),
                    source_output_index=previous_tx_vout,
                    unlocking_script_template=P2PKH().unlock(sender_private_key)
                )

    
    Additional_output = TransactionOutput(
                locking_script=P2PKH().lock("1QnWY1CWbWGeqobBBoxdZZ3DDeWUC2VLn"),
                satoshis=33,
                change=False
            )

    tx = Transaction([tx_input], outputs + [Additional_output])


    tx.fee()
    tx.sign()
```


Do you async & await for the transaction broadcast.
```python
    import asyncio

    async def main():
        try:
             # All other codes
             
            await tx.broadcast()

    except Exception as e:
    print(f"Error occurred: {str(e)}")
    
if __name__ == "__main__":
    asyncio.run(main())

```

* It automaticaly creates an oridnal, fee, and change outputs.
* The fee of inscription is less than 0.1 cent, 998 satoshi. (The commarcial license for cheaper fee rate.)
* You also have to pay the mining fee for miners, 1 satoshi/ kb of data.


## License

This library is available for individual use. For commercial use, including metadata, and parsing features, an Enterprise license is required. See [LICENSE.md](LICENSE.md) for details.