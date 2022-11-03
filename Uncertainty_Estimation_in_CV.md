### Uncertainty 是什么？

1. Aleatoric Uncertainty 随机不确定度（Data Uncertainty 数据不确定度）
2. Epistemic Uncertainty 认知不确定度（Model Uncertainty 模型不确定度）

训练好的神经网络（NN）模型，本质是一个拥有大量确定参数的函数（只有加法和乘法），不管你给什么输入，它都能给你一个输出。这会导致两种我们不愿意看到的意外情况：

- 对明明错误的预测结果，模型输出的置信度却很高；
- 对没有见过的输入(OoD，Out-of-ditribution)，比如给一个识别猫狗的模型输入一张桌子图片，模型一定会输出：这是猫 or 这是狗。

Aleatoric Uncertainty 主要出现在物体边缘和远处。该 Uncertainty 源于数据本身，主要是标注员对物体边缘标注的精度不够、远处物体成像质量较差导致。

Epistemic uncertainty 主要出现在 Model 预测不好的地方。

Epistemic uncertainty 可以通过增加数据解决。当数据点增加，模型逐渐确定，uncertainty减小。

Aleatoric Uncertainty 其就是训练数据中的噪声，来源于数据收集 or 标注过程。这些噪声是随机的，而且是固定的。噪声越多，数据的不确定度越大。它可以被测量，但是无法通过增加数据减小。

### Uncertainty 如何计算？

1. Aleatoric Uncertainty
   - Segmentation Variability Estimation (MIA 2018)
   - Probabilistic Deep Learning (NeurIPS 2017)
   - Test Time Augmentation (MIDL, MICCAI 2018)
2. Epistemic uncertainty
   - Monte Carlo Dropout (ICML 15, NeurIPS 17)
   - Deep Ensemble (NeurIPS 17)
   - M Heads (ICCV 17)
   - Probabilistic U-Net (NeruIPS 18)
   - Probabilitic Hierarchical Segmentation (MICCAI 19)

