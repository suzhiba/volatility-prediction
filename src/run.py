from method import *
from read_data import *
import os
import pickle
import time
from sklearn.preprocessing import scale
from ptm import HMM_LDA
from ptm.utils import get_top_words

# os.chdir('/Users/hengweiguo/Documents/repo/volatility-prediction/src')
#
# 
# # X_train and X_test are doc-term matrices
# # X_train_extra and X_test_extra are v-12 volatilities
# # Y's are labels
# X_train_extra, X_train, Y_train, X_test_extra, X_test, Y_test, vocab, indices = generate_train_test_set(2006, 2, 0.01)
# # # store the data
# np.savez('train_test_data_001', X_train_extra=X_train_extra, X_train=X_train, Y_train=Y_train, X_test_extra=X_test_extra, X_test=X_test, Y_test=Y_test, indices=indices)
# # save vocab seperately since it's not np array
# with open('vocab_001.pickle', 'w') as f:
#     pickle.dump([vocab], f)

# # do the lda reduction
# n_topics = 20
# n_iter = 1000
# t0 = time.time()
# X_train_lda, X_test_lda, lda_model = topic_from_LDA(X_train, X_test, n_topics, n_iter)
# t1 = time.time()
# print('lda takes time: ' + str(t1 - t0))
# np.savez('lda_data_001_20topics', X_train_lda=X_train_lda, X_test_lda=X_test_lda)
#
# with open('lda_model_001_20topics.pickle', 'w') as f:
#     pickle.dump([lda_model], f)


# Getting back the objects:
do_extra_original = 1
scaleData = 0
withextra = 0

test_differ = 0

lda_test = 0
hmm_lda_test = 0
standard_test = 1
optimize = 1

npzfile = np.load('train_test_data_01.npz')
X_train_extra = npzfile['X_train_extra']
X_train = npzfile['X_train'] # doc term mat
Y_train = npzfile['Y_train'] # doc term mat
X_test_extra = npzfile['X_test_extra']
X_test = npzfile['X_test']
Y_test = npzfile['Y_test']
indices = npzfile['indices']

# npzfile = np.load('lda_data_01_20topics.npz')
# X_train_lda = npzfile['X_train_lda']
# X_test_lda = npzfile['X_test_lda']

# with open('vocab_001.pickle') as f:
#     vocab= pickle.load(f)
#
# with open('lda_model_001_20topics.pickle') as f:
#     lda_model= pickle.load(f)[0]


# # print the lda topics
# n_top_words = 3
# topic_word = lda_model.topic_word_
# for i, topic_dist in enumerate(topic_word):
#     topic_words = np.array(vocab).T[np.argsort(topic_dist)][:-(n_top_words+1):-1]
#     topic_words = topic_words.tolist()
#     topic_words = [item for sublist in topic_words for item in sublist if item not in ['and', 'in', 'the', 'of', 'a', 'to', 'is', 'we', 'that', 'for']]
#     print('Topic {}: {}'.format(i, ' '.join(topic_words)))

hmm_lda_vocab, hmm_lda_corpus, test_count = generateDataForHmmLDA(2006, 2, indices)
hmm_lda_X_train = hmm_lda_corpus[:-test_count] # input to hmm lda reduction
hmm_lda_X_test = hmm_lda_corpus[-test_count:]

# train hmm lda
n_docs = len(hmm_lda_X_train)
n_voca = len(hmm_lda_vocab)
n_topic = 30
n_class = 10
max_iter = 100
alpha = 0.001
beta = 0.05
gamma = 0.001
eta = 0.001
hmm_lda_model = HMM_LDA(n_docs, n_voca, n_topic, n_class, alpha=alpha, beta=beta, gamma=gamma, eta=eta, verbose=True)
hmm_lda_model.fit(hmm_lda_X_train, max_iter=max_iter)
hmm_lda_test_model = hmm_lda_model.transform(hmm_lda_X_test, max_iter=max_iter)

X_train_hmm_lda = hmm_lda_model.DT / hmm_lda_model.DT.sum(axis=1)[:,None]
X_test_hmm_lda = hmm_lda_test_model.DT / hmm_lda_test_model.DT.sum(axis=1)[:,None]

with open('hmm_lda_01_30topics_10classes_100iters.pickle', 'w') as f:
    pickle.dump([hmm_lda_vocab, hmm_lda_corpus, hmm_lda_X_train, hmm_lda_X_test, hmm_lda_model, hmm_lda_test_model, X_train_hmm_lda, X_test_hmm_lda], f)

with open('hmm_lda_01_6topics_50classes_100iters.pickle') as f:
   tmpData = pickle.load(f)
   hmm_lda_vocab = tmpData[0]
   hmm_lda_corpus = tmpData[1]  # hmm_lda_X_train + hmm_LDA_X_test
   hmm_lda_X_train = tmpData[2]
   hmm_lda_X_test = tmpData[3]
   hmm_lda_model = tmpData[4]
   hmm_lda_test_model = tmpData[5]
   X_train_hmm_lda = tmpData[6]
   X_test_hmm_lda = tmpData[7]
   del tmpData




# print hmm lda topics
for ti in range(n_topic):
    top_words = get_top_words(hmm_lda_model.TW, hmm_lda_vocab, ti, n_words=3)
    print('Topic', ti ,': ', ','.join(top_words))


# print hmm lda syntactic words
for ci in range(1, n_class):
    top_words = get_top_words(hmm_lda_model.CW, hmm_lda_vocab, ci, n_words=3)
    print('Class', ci ,': ', ','.join(top_words))


tfidf_train, tfidf_test = dtm_to_tfidf(X_train, X_test)
#tfidf_train = 0
#tfidf_test = 0

if do_extra_original:
    tf_train, tf_test = dtm_to_tf(X_train, X_test)
    log1p_train, log1p_test = dtm_to_log1p(X_train, X_test)
else:
    tf_train = 0
    tf_test = 0
    log1p_train = 0
    log1p_test = 0

X_train_lsi, X_test_lsi = topic_from_LSI(X_train, X_test, 20)

if scaleData:
    # can't do with_mean=True with sparse matrix
    tf_train = scale(tf_train, with_mean=False)
    tf_test = scale(tf_test, with_mean=False)
    tfidf_train = scale(tfidf_train, with_mean=False)
    tfidf_test = scale(tfidf_test, with_mean=False)
    log1p_train = scale(log1p_train, with_mean=False)
    log1p_test = scale(log1p_test, with_mean=False)
    X_train_lda = scale(X_train_lda, with_mean=False)
    X_test_lda = scale(X_test_lda, with_mean=False)

# combine the doc-term data and the voliatility data
if withextra and do_extra_original:
    X_total_train_tf = combine_extra_to_train(X_train_extra, tf_train)
    X_total_test_tf = combine_extra_to_train(X_test_extra, tf_test)

    X_total_train_tfidf = combine_extra_to_train(X_train_extra, tfidf_train)
    X_total_test_tfidf = combine_extra_to_train(X_test_extra, tfidf_test)

    X_total_train_log1p = combine_extra_to_train(X_train_extra, log1p_train)
    X_total_test_log1p = combine_extra_to_train(X_test_extra, log1p_test)

    X_total_train_lda= combine_extra_to_train(X_train_extra, X_train_lda)
    X_total_test_lda = combine_extra_to_train(X_test_extra, X_test_lda)

    X_total_train_lsi = combine_extra_to_train(X_train_extra, X_train_lsi)
    X_total_test_lsi = combine_extra_to_train(X_test_extra, X_test_lsi)

    X_total_train_hmm_lda= combine_extra_to_train(X_train_extra, X_train_hmm_lda)
    X_total_test_hmm_lda = combine_extra_to_train(X_test_extra, X_test_hmm_lda)

else:    
    X_total_train_tf = tf_train
    X_total_test_tf = tf_test

    X_total_train_tfidf = tfidf_train
    X_total_test_tfidf = tfidf_test

    X_total_train_log1p = log1p_train
    X_total_test_log1p = log1p_test

    X_total_train_lda= X_train_lda
    X_total_test_lda = X_test_lda

    X_total_train_lsi = X_train_lsi
    X_total_test_lsi = X_test_lsi

    X_total_train_hmm_lda= X_train_hmm_lda
    X_total_test_hmm_lda = X_test_hmm_lda


# Code for predicting difference

if test_differ:
    Y_train = Y_train - X_train_extra
    Y_test = Y_test - X_test_extra
    X_test_extra = np.zeros(len(X_test_extra))

# -------- Find thehyper parameters ----------
# n_iter_search = 20
# t0 = time.time()
# mse_tf_plus, random_search_tf_plus = optimize_svr(X_total_train_tf, Y_train, X_total_test_tf, Y_test, n_iter_search)
# t1 = time.time()
# print('tune hyper parameter for tf+ takes time: ' + str(t1 - t0))
#-------------------------- Training and Testing ---------------------------

# train and test with the baseline: V-12
t0 = time.time()
mse_V_minus_12 = baseline(X_test_extra, Y_test)
t1 = time.time()
print('mse_V_minus_12 takes time: ' + str(t1 - t0))
print('mse_V_minus_12: ' + str(mse_V_minus_12))

# Train LDA and test it

if lda_test:
    n_topics = 20
    n_iter = 1000
    for n_topics in [6, 15, 30, 50]:
        for alpha in [0.001]:
            for eta in [0.05]:
                # Best alpha = 0.001
                # Best eta = 0.05
                t0 = time.time()
                X_total_train_lda, X_total_test_lda, lda_model = topic_from_LDA(X_train, X_test, n_topics, n_iter, alpha, eta)
                t1 = time.time()
                print('lda takes time: ' + str(t1 - t0))
                mse_V_lda = involk_svr(X_total_train_lda, Y_train, X_total_test_lda, Y_test, degree=2)
                print('mse_V_lda: ' + str(mse_V_lda))
                print('n_topics = ' + str(n_topics))
                print('alpha = ' + str(alpha))
                print('eta = ' + str(eta))
                print('=========================================')
                del lda_model


if hmm_lda_test:
    n_topics = 20
    max_iter = 100
    for n_topics in [6, 15, 30, 50]:
        for n_class in [6, 15, 30, 50]:

            t0 = time.time()
            # train hmm lda
            n_docs = len(hmm_lda_X_train)
            n_voca = len(hmm_lda_vocab)
            alpha = 0.01
            beta = 0.01
            gamma = 0.01
            eta = 0.01
            hmm_lda_model = HMM_LDA(n_docs, n_voca, n_topics, n_class, alpha=alpha, beta=beta, gamma=gamma, eta=eta, verbose=False)
            hmm_lda_model.fit(hmm_lda_X_train, max_iter=max_iter)
            hmm_lda_test_model = hmm_lda_model.transform(hmm_lda_X_test, max_iter=max_iter)

            X_total_train_hmm_lda = hmm_lda_model.DT / hmm_lda_model.DT.sum(axis=1)[:,None]
            X_total_test_hmm_lda = hmm_lda_test_model.DT / hmm_lda_test_model.DT.sum(axis=1)[:,None]

            t1 = time.time()
            print('hmm_lda takes time: ' + str(t1 - t0))
            for degree in [1,2,3]:
                mse_V_hmm_lda = involk_svr(X_total_train_hmm_lda, Y_train, X_total_test_hmm_lda, Y_test, degree=degree)
                print('mse_V_hmm_lda: ' + str(mse_V_hmm_lda))
                print('n_topics = ' + str(n_topics))
                print('n_classes  = ' + str(n_class))
                print('degree  = ' + str(degree))
                print('=========================================')
            del hmm_lda_model, hmm_lda_test_model

# Test All

def do_svr(name, X_train, Y_train, X_test, Y_test, optimize, degree, C):
    if optimize:
        mse_V, params = optimize_svr(X_train, Y_train, X_test, Y_test)
        print('SVR params: ' + str(params))
    else:
        mse_V = involk_svr(X_train, Y_train, X_test, Y_test, degree=degree, C=C)
    print('mse_V_' + name + ': ' + str(mse_V))


if standard_test:
    if lda_test:
        do_svr('lda', X_total_train_lda, Y_train, X_total_test_lda, Y_test, optimize, 2, 1e5)

    if hmm_lda_test:
        do_svr('hmm_lda', X_train_hmm_lda, Y_train, X_test_hmm_lda, Y_test, optimize, 2, 1e4)

    do_svr('lsi', X_total_train_lsi, Y_train, X_total_test_lsi, Y_test, optimize, 2, 1e4)
    do_svr('tfidf', X_total_train_tfidf, Y_train, X_total_test_tfidf, Y_test, optimize, 1, 1e5)

    if do_extra_original:
        do_svr('tf', X_total_train_tf, Y_train, X_total_test_tf, Y_test, optimize, 1, 1)
        do_svr('log1p', X_total_train_log1p, Y_train, X_total_test_log1p, Y_test, optimize, 1, 1)
        do_svr('lsi_log1p', X_total_train_lsi_log1p, Y_train, X_total_test_lsi_log1p, Y_test, optimize, 2, 1e4)
    
    # train and test with HMM-LDA
    # t0 = time.time()
    #mse_V_lda = involk_svr(X_train_hmmlda, Y_train, X_test_hmmlda, Y_test)
    # mse_V_lda, params = optimize_svr(X_train_hmmlda, Y_train, X_test_hmmlda, Y_test)
    # t1 = time.time()
    # print('mse_V_hmmlda takes time: ' + str(t1 - t0))
    # print('mse_V_hmmlda: ' + str(mse_V_lda))
    # print('SVR params: '+ str(params))

import report_on_finish
