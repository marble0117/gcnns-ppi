import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.modules.module import Module


class GCN(nn.Module):
    def __init__(self, nfeat, nclass, nhid, dropout):
        super(GCN, self).__init__()
        self.gc1 = GCNConv(nfeat, nhid)
        self.gc2 = GCNConv(nhid, nhid)
        self.gc3 = GCNConv(nhid, nclass)
        self.dropout = dropout

    def reset_parameters(self):
        self.gc1.reset_parameters()
        self.gc2.reset_parameters()
        self.gc3.reset_parameters()

    def forward(self, data):
        x = data.features
        adj = data.adj
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = F.relu(self.gc1(x, adj))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = F.relu(self.gc2(x, adj))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.gc3(x, adj)
        return torch.sigmoid(x)


class GCNConv(Module):
    def __init__(self, in_features, out_features, bias=True):
        super(GCNConv, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight.data, gain=1.414)
        if self.bias is not None:
            self.bias.data.fill_(0)

    def forward(self, x, adj):
        x = torch.matmul(x, self.weight)
        x = torch.spmm(adj, x)
        if self.bias is not None:
            x += self.bias
        return x


def create_gcn_model(nfeat, nclass, nhid=128, dropout=0.5):
    model = GCN(nfeat, nclass, nhid, dropout)
    return model
