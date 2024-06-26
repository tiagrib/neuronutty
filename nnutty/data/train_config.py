from dataclasses import dataclass, fields
from pathlib import Path

@dataclass
class TrainConfig:
    preprocessed_path: str
    save_model_path: str
    batch_size: int = 64
    shuffle: bool = False
    hidden_dim: int = 1024
    num_layers: int = 1
    num_heads: int = 4
    save_model_frequency: int = 5
    epochs: int = 100
    device: str = 'cuda'
    architecture: str = 'seq2seq'
    lr: float = None
    optimizer: str = 'sgd'
    representation: str = 'aa'
    interpolative: bool = False

    REQUIRED_FIELDS = ['preprocessed_path', 'save_model_path']

    def __init__(self, **kwargs):
        for field in fields(self):
            setattr(self, field.name, kwargs.get(field.name, None))

    def __post_init__(self):
        if self.b is None:
            self.b = 'Bravo'
        if self.c is None:
            self.c = 'Charlie'

    def _get_kwargs(self):
        return [(field.name, getattr(self, field.name)) for field in fields(self)]
    
    def __iter__(self):
        return iter(self._get_kwargs())
    
    def keys(self):
        return [field.name for field in fields(self)]
    
    def __getitem__(self, item):
        return getattr(self, item)
    
    def get_preprocessed_path(self):
        if hasattr(self, 'interpolative') and self.interpolative:
            return Path(self.preprocessed_path) / (self.representation + '_interpolative')
        return Path(self.preprocessed_path) / self.representation

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        config = {}
        for line in lines:
            line_split = line.strip().split(':')
            key, value = line_split[0], ':'.join(line_split[1:])
            key = key.replace('-', '_')
            if value.lower() == 'none':
                value = None
            elif '.' in value and value.replace(".", "").isnumeric():
                value = float(value)
            elif value.isdigit():
                value = int(value)
            elif value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            config[key] = value

        for required_field in TrainConfig.REQUIRED_FIELDS:
            if required_field not in config:
                raise ValueError(f"Missing required field '{required_field}' in config file '{file_path}'!")
            
        if not 'representation' in config:
            if Path(config['preprocessed_path']).name in ['aa', 'rotmat']:
                config['representation'] = Path(config['preprocessed_path']).name
                config['preprocessed_path'] = Path(config['preprocessed_path']).parent
            else:
                config['representation'] = 'aa'

        return cls(**config)
