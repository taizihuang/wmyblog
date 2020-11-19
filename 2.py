data = open('2.txt').read()
count = {}
for c in data:
	count[c]=count.get(c,0)+1
print(count)
