import kagglehub

path = kagglehub.dataset_download("pradeepjangirml007/laptop-data-set")

print(f"Dataset downloaded to: {path}")
print("Please inspect this directory to find the actual CSV file name.")