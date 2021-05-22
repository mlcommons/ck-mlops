/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#include "ck_nntest_caffe_conv.h"

using namespace caffe;

int main() {
  Caffe::set_mode(Caffe::GPU);
  Caffe::SetDevice(0);

  CK::Caffe::test_convolution(true);

  return 0;
}
