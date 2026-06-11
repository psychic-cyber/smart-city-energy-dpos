from database.mongodb.blockchain_repository import get_blocks

blocks = get_blocks(5)

for block in blocks:
    print(type(block))
    print(block)
    print("================================")



from database.mongodb.blockchain_repository import get_blocks

blocks = get_blocks(100)

print(blocks[-1])
