from blockchain.dpos.delegate import Delegate
from blockchain.dpos.consensus import DPoSConsensus


consensus = DPoSConsensus()

consensus.register_delegate(
    Delegate(
        1,
        "District-A",
        150
    )
)

consensus.register_delegate(
    Delegate(
        2,
        "District-B",
        300
    )
)

consensus.register_delegate(
    Delegate(
        3,
        "District-C",
        450
    )
)

consensus.register_delegate(
    Delegate(
        4,
        "District-D",
        250
    )
)

consensus.register_delegate(
    Delegate(
        5,
        "District-E",
        100
    )
)

print("\nRegistered Delegates:\n")

for delegate in consensus.delegates:

    print(
        delegate.to_dict()
    )

print(
    "\nTop Delegate:"
)

print(
    consensus.get_top_delegate().to_dict()
)

print(
    "\nSelected Validator:"
)

print(
    consensus.select_delegate().to_dict()
)
