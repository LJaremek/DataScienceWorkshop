import os

from torch.utils.data import Dataset
from PIL import Image


class ScrapDataset(Dataset):
    def __init__(
            self,
            images: dict[str, str],
            root_dir: str = "./data"
            ) -> None:
        """
        Args:
            root_dir (string): Ścieżka do folderu "data"
        """
        self.root_dir = root_dir

        self.data_dirs = [
            os.path.join(root_dir, d) for d in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, d)) and d.isdigit()
        ]
        self.data_dirs.sort(key=lambda x: int(os.path.basename(x)))

        self.images = images

    def __len__(self) -> int:
        return len(self.data_dirs)

    def __getitem__(self, idx: int) -> dict[str, Image.Image]:
        data_dir = self.data_dirs[idx]

        sample = {}

        for image_type_name, image_name in self.images.items():
            path = os.path.join(data_dir, image_name)

            img = None
            if os.path.exists(path):
                img = Image.open(path).convert("RGB")

            sample[image_name] = img

        return sample
