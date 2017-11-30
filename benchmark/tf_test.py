'''
' @file      tf_test.py
' @author    zhangshu(shu.zhang@intel.com)
' @date      2017-11-26 16:12:45
' @brief
'''

import numpy as np
import tensorflow as tf
from tensorflow.contrib import rnn
from tensorflow.python.ops import array_ops
import intel_lstm

#sizes = [[16, 50, 1024, 1024]]
sizes = [[3, 9, 3, 3]]

for size in sizes:
    g = tf.Graph()
    with g.as_default():
        N, T, D, H = size
        x_input = tf.Variable(tf.random_uniform([T, N, D]))
        y_target = np.random.rand(N, H).astype(np.float32)
        h0 = tf.zeros(shape=[N, H])
        c0 = tf.zeros(shape=[N, H])

        tf_cell = rnn.BasicLSTMCell(H, forget_bias=0.0, state_is_tuple = True)
        tf_hout, _ = rnn.static_rnn(tf_cell, tf.unstack(x_input, T), dtype=tf.float32)  #forward
        tf_cost = tf.reduce_sum((tf_hout[-1] - y_target) ** 2)

        optim = tf.train.GradientDescentOptimizer(0.01)
        tf_grad = optim.compute_gradients(tf_cost)
        tmp = [grad for (grad,v) in tf_grad]
        tf_dw = tmp[1]
        tf_db = tmp[2]
        tf_dx = tmp[0]

        tf_train_op = optim.minimize(tf_cost)


    with tf.Session(graph=g) as sess:    
        sess.run(tf.global_variables_initializer())
        sess.run(tf_hout[-1])
        print("tf_out1 = ")
        print(sess.run(tf_hout[-1]))

        intel_cell = intel_lstm.LSTM(D, H)
        intel_cell.w_x, intel_cell.w_h = array_ops.split(tf_cell.weights[0], [D, H], 0)
        intel_cell.bias = tf_cell.weights[1]
        intel_hout, _ = intel_cell.inference(x_input, h0, c0)
        tmp_out = tf.unstack(intel_hout, T)
        intel_cost = tf.reduce_sum((tmp_out[-1] - y_target) ** 2)
        intel_train_op = optim.minimize(intel_cost)
        intel_opt = tf.train.GradientDescentOptimizer(0.01)
        intel_grad = intel_opt.compute_gradients(intel_cost)
        
        print("intel_out1 = ")
        print(sess.run(intel_hout))
        sess.run(intel_grad[0:3])
    #    sess.run(intel_train_op)

    #    sess.run(tf_train_op)
    #    print("tf_out2 = ")
    #    print(sess.run(tf_hout[-1]))
    #    print("intel_out2 = ")
    #    print(sess.run(intel_hout))

        print("tf_grad=")
        print(tf_grad)
        print("tf_dw=")
        print(sess.run(tf_dw))
        print("tf_db=")
        print(sess.run(tf_db))
        print("tf_dx=")
        print(sess.run(tf_dx))



    #    print(x_input.eval())
     #   print("orig_para")
     #   print(intel_cell.w_x.eval())
     #   print(intel_cell.w_h.eval())

   #     cmp_tf = tf.stack(tf_hout).eval()
   #     cmp_intel = intel_hout.eval()
   #     print("tf_out = ", cmp_tf)
   #     print("intel_out = ", cmp_intel)
   #     ret = np.allclose(cmp_tf, cmp_intel, 0.01, 1e-4)
   #     print("Forward check = ", ret)

   #     print("tf_weight=", tf_cell.weights[0].eval())
   #     print("tf_bias=", tf_cell.weights[1].eval())
   #     
   #     intel_weight = array_ops.concat([intel_cell.w_x, intel_cell.w_h], 0).eval()
   #     print("intel_weight=", intel_weight)
   #     print("intel_bias=", intel_cell.bias.eval())

   #     ret = np.allclose(tf_cell.weights[0].eval(), intel_weight, 0.01, 1e-4)
   #     print("train weight check = ", ret)
   #     ret = np.allclose(tf_cell.weights[1].eval(), intel_cell.bias.eval(), 0.01, 1e-4)
   #     print("train bias check = ", ret)
