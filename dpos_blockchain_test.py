from blockchain.core.blockchain import Blockchain
from blockchain.dpos.delegate import Delegate
from blockchain.dpos.consensus import DPoSConsensus


blockchain = Blockchain()

consensus = DPoSConsensus()

consensus.register_delegate(
    Delegate(1, "District-A", 150)
)

consensus.register_delegate(
    Delegate(2, "District-B", 300)
)

consensus.register_delegate(
    Delegate(3, "District-C", 450)
)

transaction = {
    "entity": "Hospital-01",
    "energy": 500
}

selected_delegate = (
    consensus.select_delegate()
)

blockchain.add_block(
    transaction,
    selected_delegate.district
)

blockchain.display_chain()

print(
    "\nSelected Validator:",
    selected_delegate.district
)

print(
    "\nChain Valid:",
    blockchain.is_chain_valid()
)
