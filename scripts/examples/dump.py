my_list = ['A', 'B', 'C', 'D', 'E']

# Delete all items in the list after the item with the value 'D'

new_list = []
for item in my_list:
    new_list.append(item)
    if item == 'C':
        break

print(new_list)
# Output: ['A', 'B', 'C']
