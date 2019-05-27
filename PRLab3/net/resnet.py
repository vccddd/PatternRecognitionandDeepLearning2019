import torch.nn as nn
import torch.nn.functional as fun


class ResBlock(nn.Module):
    def __init__(self, in_channel, out_channel, stride=1, shortcut=None):
        super(ResBlock, self).__init__()
        self.left = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, 3, stride, 1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(True),
            nn.Conv2d(out_channel, out_channel, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channel)
        )
        self.right = shortcut

    def forward(self, x):
        out = self.left(x)
        residual = x if self.right is None else self.right(x)
        out += residual
        return fun.relu(out)


class ResNet(nn.Module):

    def __init__(self):
        super().__init__()
        self.pre = nn.Sequential(
            nn.Conv2d(3, 64, 7, 2, 3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(3, 2, 1)
        )
        self.layer1 = self.make_layer(64, 64, 2)
        self.layer2 = self.make_layer(64, 128, 2, stride=2)
        self.layer3 = self.make_layer(128, 256, 2, stride=2)
        self.layer4 = self.make_layer(256, 512, 2, stride=2)
        self.avg_pool = nn.AvgPool2d(7)
        self.full_conn = nn.Linear(512, 10)

    def make_layer(self, inputs, outputs, block_num, stride=1):
        shortcut = nn.Sequential(
            nn.Conv2d(inputs, outputs, 1, stride),
            nn.BatchNorm2d(outputs)
        )
        layers = []
        layers.append(ResBlock(inputs, outputs, stride, shortcut))

        for i in range(1, block_num):
            layers.append(ResBlock(outputs, outputs))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.pre(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.full_conn(x)
        return x

