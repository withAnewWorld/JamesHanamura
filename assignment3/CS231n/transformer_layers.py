from numpy import iinfo
import torch
import torch.nn as nn
from torch.nn import functional as F
import math

"""
This file defines layer types that are commonly used for transformers.
"""

class PositionalEncoding(nn.Module):
    """
    Encodes information about the positions of the tokens in the sequence. In
    this case, the layer has no learnable parameters, since it is a simple
    function of sines and cosines.
    """
    def __init__(self, embed_dim, dropout=0.1, max_len=5000):
        """
        Construct the PositionalEncoding layer.

        Inputs:
         - embed_dim: the size of the embed dimension
         - dropout: the dropout value
         - max_len: the maximum possible length of the incoming sequence
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        assert embed_dim % 2 == 0
        # Create an array with a "batch dimension" of 1 (which will broadcast
        # across all examples in the batch).
        pe = torch.zeros(1, max_len, embed_dim)
        ############################################################################
        # TODO: Construct the positional encoding array as described in            #
        # Transformer_Captioning.ipynb.  The goal is for each row to alternate     #
        # sine and cosine, and have exponents of 0, 0, 2, 2, 4, 4, etc. up to      #
        # embed_dim. Of course this exact specification is somewhat arbitrary, but #
        # this is what the autograder is expecting. For reference, our solution is #
        # less than 5 lines of code.                                               #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        
        i=torch.arange(0, max_len).reshape(max_len, -1)
        j= 10000**-(torch.arange(0, 1, 2/embed_dim))
        pe[0, :, torch.arange(0, embed_dim, 2)]= torch.sin(i*j)
        pe[0, :, torch.arange(1, embed_dim, 2)]= torch.cos(i*j)


        ##################### naive version ####################################

        # for i in range(int(embed_dim//2)):
        #   for pos in range(max_len):
        #     pe[0, pos, 2*i] = math.sin(pos*10000**(-2*i/embed_dim))
        #     pe[0, pos, 2*i+1] = math.cos(pos*10000**(-(2*i)/embed_dim))
        

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # Make sure the positional encodings will be saved with the model
        # parameters (mostly for completeness).
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Element-wise add positional embeddings to the input sequence.

        Inputs:
         - x: the sequence fed to the positional encoder model, of shape
              (N, S, D), where N is the batch size, S is the sequence length and
              D is embed dim
        Returns:
         - output: the input sequence + positional encodings, of shape (N, S, D)
        """
        N, S, D = x.shape
        # Create a placeholder, to be overwritten by your code below.
        output = torch.empty((N, S, D))
        ############################################################################
        # TODO: Index into your array of positional encodings, and add the         #
        # appropriate ones to the input sequence. Don't forget to apply dropout    #
        # afterward. This should only take a few lines of code.                    #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
  
        output= x+self.pe[:, :S, :]
        output = self.dropout(output)

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################
        return output


class MultiHeadAttention(nn.Module):
    """
    A model layer which implements a simplified version of masked attention, as
    introduced by "Attention Is All You Need" (https://arxiv.org/abs/1706.03762).

    Usage:
      attn = MultiHeadAttention(embed_dim, num_heads=2)

      # self-attention
      data = torch.randn(batch_size, sequence_length, embed_dim)
      self_attn_output = attn(query=data, key=data, value=data)

      # attention using two inputs
      other_data = torch.randn(batch_size, sequence_length, embed_dim)
      attn_output = attn(query=data, key=other_data, value=other_data)
    """

    def __init__(self, embed_dim, num_heads, dropout=0.1):
        """
        Construct a new MultiHeadAttention layer.

        Inputs:
         - embed_dim: Dimension of the token embedding
         - num_heads: Number of attention heads
         - dropout: Dropout probability
        """
        super().__init__()
        assert embed_dim % num_heads == 0

        # We will initialize these layers for you, since swapping the ordering
        # would affect the random number generation (and therefore your exact
        # outputs relative to the autograder). Note that the layers use a bias
        # term, but this isn't strictly necessary (and varies by
        # implementation).
        self.key = nn.Linear(embed_dim, embed_dim)
        self.query = nn.Linear(embed_dim, embed_dim)
        self.value = nn.Linear(embed_dim, embed_dim)
        self.proj = nn.Linear(embed_dim, embed_dim)
        
        ############################################################################
        # TODO: Initialize any remaining layers and parameters to perform the      #
        # attention operation as defined in Transformer_Captioning.ipynb. We will  #
        # also apply dropout just after the softmax step. For reference, our       #
        # solution is less than 5 lines.                                           #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        self.softmax = nn.Softmax(dim=-1)
        self.h = num_heads
        self.drop = nn.Dropout(p=dropout)
        

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def forward(self, query, key, value, attn_mask=None):
        """
        Calculate the masked attention output for the provided data, computing
        all attention heads in parallel.

        In the shape definitions below, N is the batch size, S is the source
        sequence length, T is the target sequence length, and E is the embedding
        dimension.

        Inputs:
        - query: Input data to be used as the query, of shape (N, S, E)
        - key: Input data to be used as the key, of shape (N, T, E)
        - value: Input data to be used as the value, of shape (N, T, E)
        - attn_mask: Array of shape (T, S) where mask[i,j] == 0 indicates token
          i in the target should not be influenced by token j in the source.

        Returns:
        - output: Tensor of shape (N, S, E) giving the weighted combination of
          data in value according to the attention weights calculated using key
          and query.
        """
        N, S, D = query.shape
        N, T, D = value.shape
        # Create a placeholder, to be overwritten by your code below.
        output = torch.empty((N, T, D))
        ############################################################################
        # TODO: Implement multiheaded attention using the equations given in       #
        # Transformer_Captioning.ipynb.                                            #
        # A few hints:                                                             #
        #  1) You'll want to split your shape from (N, T, E) into (N, T, H, E/H),  #
        #     where H is the number of heads.                                      #
        #  2) The function torch.matmul allows you to do a batched matrix multiply.#
        #     For example, you can do (N, H, T, E/H) by (N, H, E/H, T) to yield a  #
        #     shape (N, H, T, T). For more examples, see                           #
        #     https://pytorch.org/docs/stable/generated/torch.matmul.html          #
        #  3) For applying attn_mask, think how the scores should be modified to   #
        #     prevent a value from influencing output. Specifically, the PyTorch   #
        #     function masked_fill may come in handy.                              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        
        ################## vectorized version ##################################

        query = self.query(query).view(N, S, self.h, D//self.h)
        key = self.key(key).view(N, T, self.h, int(D/self.h))
        value = self.value(value).view(N, T, self.h, int(D/self.h))

        XQ_i = query.transpose(1, 2)
        XK_i = key.transpose(1, 2)
        XV_i = value.transpose(1, 2)
        Y=torch.empty((N, self.h, T, T))

        alignment=torch.matmul(XQ_i, XK_i.transpose(2, 3))/math.sqrt(D/self.h)
        if attn_mask != None:
          alignment = alignment.masked_fill(attn_mask==False, -float('inf'))
        attention=self.softmax(alignment)
        Y= self.drop(attention)
        Y= torch.matmul(Y, XV_i)
        
        concat =Y.transpose(1, 2).contiguous().view(N, -1, D)
        output= self.proj(concat)
        
        #########################  Naive version  #############################
        # 안됨

        # XQ = self.query(query)
        # XK = self.key(key)
        # XV = self.value(value)

        # XQ = XQ.reshape((N, S, self.h, D//self.h)).transpose(1, 2)
        # XK = XK.reshape((N, T, self.h, D//self.h)).transpose(1, 2)
        # XV = XV.reshape((N, T, self.h, D//self.h)).transpose(1, 2)

        # for n in range(N):
        #   Y=torch.empty((self.h, T, D//self.h))
        #   for i in range(self.h):
        #     XQ_i = XQ[n, i, :, :]
        #     XK_i = XK[n, i, :, :]
        #     XV_i = XV[n, i, :, :]
        #     alignment = torch.matmul(XQ_i, XK_i.T)/math.sqrt(D/self.h)
        #     if attn_mask != None:
        #       alignment = alignment.masked_fill(attn_mask==False, -float('inf'))
        #     attention = self.softmax(alignment)
        #     Y_i = self.drop(attention)
        #     Y[i, :, :]=torch.matmul(Y_i, XV_i)
        #   output[n, :, :] = self.proj(Y.transpose(0, 1).reshape(T, D))
          
             
        
        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################
        return output


