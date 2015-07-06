from nengo.utils.network import with_self

__author__ = 'Petrut Bogdan'
import nengo
from nengo import Network
from nengo.dists import Choice
import numpy as np


def _product(x):
    return x[0] * x[1]


class MatrixMultiplication(Network):
    def __init__(self, n_neurons, matrix_like_A, matrix_like_B,
                 ens_dimensions_A=1, ens_dimensions_B=1, radius=1.0,
                 label=None, seed=None,
                 add_to_container=None, **ens_kwargs):
        """
        This class is designed for easy matrix multiplication using Nengo.

        Use:
        :param n_neurons:
        :type n_neurons:
        :param matrix_like_A:
        :type matrix_like_A:
        :param matrix_like_B:
        :type matrix_like_B:
        :param ens_dimensions_A:
        :type ens_dimensions_A:
        :param ens_dimensions_B:
        :type ens_dimensions_B:
        :param label:
        :type label:
        :param seed:
        :type seed:
        :param add_to_container:
        :type add_to_container:
        :param ens_kwargs:
        :type ens_kwargs:
        :return:
        :rtype:
        """
        super(MatrixMultiplication, self).__init__(label, seed,
                                                   add_to_container)
        self.config[nengo.Ensemble].update(ens_kwargs)

        label_prefix = "" if label is None else label + "_"

        self.n_neurons = n_neurons
        self.n_ensembles_A = matrix_like_A.size
        self.n_ensembles_B = matrix_like_B.size
        self.dimensions_per_ensemble_A = ens_dimensions_A
        self.dimensions_per_ensemble_B = ens_dimensions_B
        self.matrix_like_A = matrix_like_A
        self.matrix_like_B = matrix_like_B
        self.radius = radius

        with self:
            self.input_A = nengo.Node(size_in=self.dimensions_A,
                                      label="input A")
            self.input_B = nengo.Node(size_in=self.dimensions_B,
                                      label="input B")

            self.A = nengo.networks.EnsembleArray(self.n_neurons,
                                                  matrix_like_A.size,
                                                  radius=self.radius)
            self.B = nengo.networks.EnsembleArray(self.n_neurons,
                                                  matrix_like_B.size,
                                                  radius=self.radius)
            nengo.Connection(self.input_A, self.A.input)
            nengo.Connection(self.input_B, self.B.input)

            self.C = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_like_A.size * self.matrix_like_B.shape[
                    1],
                ens_dimensions=2,
                radius=1.5 * self.radius,
                encoders=Choice([[1, 1], [-1, 1], [1, -1], [-1, -1]]))

        transform_a = np.zeros((self.C.dimensions, self.matrix_like_A.size))
        transform_b = np.zeros((self.C.dimensions, self.matrix_like_B.size))

        for i in range(self.matrix_like_A.shape[0]):
            for j in range(self.matrix_like_A.shape[1]):
                for k in range(self.matrix_like_B.shape[1]):
                    tmp = (j + k * self.matrix_like_A.shape[
                        1] + i * self.matrix_like_B.size)
                    transform_a[tmp * 2][
                        j + i * self.matrix_like_A.shape[1]] = 1
                    transform_b[tmp * 2 + 1][
                        k + j * self.matrix_like_B.shape[1]] = 1

        with self:
            nengo.Connection(self.A.output, self.C.input, transform=transform_a)
            nengo.Connection(self.B.output, self.C.input, transform=transform_b)
            self.D = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_like_A.shape[0] *
                            self.matrix_like_B.shape[1],
                radius=self.radius)

        transform_c = np.zeros((self.D.dimensions, self.matrix_like_B.size))

        for i in range(self.matrix_like_B.size):
            transform_c[i // self.matrix_like_B.shape[0]][i] = 1

        with self:
            _prod = self.C.add_output("product", _product)
            nengo.Connection(_prod, self.D.input, transform=transform_c)
            # The magic result
            self.output_result = nengo.Node(
                size_in=matrix_like_A.shape[0] * matrix_like_B.shape[1],
                label="Output")
            nengo.Connection(self.D.output, self.output_result)

    @property
    def dimensions_A(self):
        return self.n_ensembles_A * self.dimensions_per_ensemble_A

    @property
    def dimensions_B(self):
        return self.n_ensembles_B * self.dimensions_per_ensemble_B


if __name__ == "__main__":
    test = MatrixMultiplication(50, np.asarray([[1]]), np.asarray([[1, 2, 3]]))
