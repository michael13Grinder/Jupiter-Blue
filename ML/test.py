import numpy as np

arr = np.array([[1, 2, 3], [4, 5, 6], [4, 5, 6]])
file = open("file1.txt", "w+")
content = str(arr).replace('[', '').replace(']', '').replace('\n ', '\n')
file.write(content)
file.close()

data = np.loadtxt("file1.txt", dtype=int)
print(data)