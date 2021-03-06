
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Free University
# Berlin, 14195 Berlin, Germany.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

r"""Unit tests for matrix API-functions

.. moduleauthor:: B.Trendelkamp-Schroer <benjamin DOT trendelkamp-schroer AT fu-berlin DOT de>

"""
import os
import unittest

import numpy as np
import scipy.sparse

from pyemma.msm.io import read_matrix, write_matrix, load_matrix, save_matrix

################################################################################
# util
################################################################################

from os.path import abspath, join
from os import pardir

testpath = abspath(join(abspath(__file__), pardir)) + '/testfiles/'

################################################################################
# ascii
################################################################################

################################################################################
# dense
################################################################################

class TestReadMatrixDense(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'matrix_int.dat'
        self.filename_float = testpath + 'matrix_float.dat'
        self.filename_complex = testpath + 'matrix_complex.dat'

        self.A_int = np.loadtxt(self.filename_int, dtype=np.int)
        self.A_float = np.loadtxt(self.filename_float, dtype=np.float)
        self.A_complex = np.loadtxt(self.filename_complex, dtype=np.complex)

    def tearDown(self):
        pass

    def test_read_matrix(self):
        A = read_matrix(self.filename_int, dtype=np.int)
        self.assertTrue(np.all(A == self.A_int))

        A = read_matrix(self.filename_float)
        self.assertTrue(np.all(A == self.A_float))

        A = read_matrix(self.filename_complex, dtype=np.complex)
        self.assertTrue(np.all(A == self.A_complex))


class TestWriteMatrixDense(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'matrix_int_out.dat'
        self.filename_float = testpath + 'matrix_float_out.dat'
        self.filename_complex = testpath + 'matrix_complex_out.dat'

        self.A_int = np.arange(3 * 3).reshape(3, 3)
        self.A_float = 1.0 * self.A_int
        self.A_complex = np.arange(3 * 3).reshape(3, 3) + \
                         1j * np.arange(9, 3 * 3 + 9).reshape(3, 3)

    def tearDown(self):
        os.remove(self.filename_int)
        os.remove(self.filename_float)
        os.remove(self.filename_complex)

    def test_write_matrix_dense(self):
        write_matrix(self.filename_int, self.A_int, fmt='%d')
        An = np.loadtxt(self.filename_int, dtype=np.int)
        self.assertTrue(np.all(An == self.A_int))

        write_matrix(self.filename_float, self.A_float)
        An = np.loadtxt(self.filename_int)
        self.assertTrue(np.all(An == self.A_float))

        write_matrix(self.filename_complex, self.A_complex)
        An = np.loadtxt(self.filename_complex, dtype=np.complex)
        self.assertTrue(np.all(An == self.A_complex))


################################################################################
# sparse
################################################################################

class TestReadMatrixSparse(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'spmatrix_int.coo.dat'
        self.filename_float = testpath + 'spmatrix_float.coo.dat'
        self.filename_complex = testpath + 'spmatrix_complex.coo.dat'

        """Reference matrices in dense storage"""
        self.reference_int = testpath + 'spmatrix_int_reference.dat'
        self.reference_float = testpath + 'spmatrix_float_reference.dat'
        self.reference_complex = testpath + 'spmatrix_complex_reference.dat'

    def tearDown(self):
        pass

    def test_read_matrix_sparse(self):
        A = np.loadtxt(self.reference_int, dtype=np.int)
        A_n = read_matrix(self.filename_int, dtype=np.int).toarray()
        self.assertTrue(np.all(A == A_n))

        A = np.loadtxt(self.reference_float)
        A_n = read_matrix(self.filename_float).toarray()
        self.assertTrue(np.all(A == A_n))

        A = np.loadtxt(self.reference_complex, dtype=np.complex)
        A_n = read_matrix(self.filename_complex, dtype=np.complex).toarray()
        self.assertTrue(np.all(A == A_n))


class TestWriteMatrixSparse(unittest.TestCase):
    def is_integer(self, x):
        """Check if elements of an array can be represented by integers.
        
        Parameters 
        ----------
        x : ndarray
            Array to check.
        
        Returns
        -------
        is_int : ndarray of bool
            is_int[i] is True if x[i] can be represented
            as int otherwise is_int[i] is False.
        
        """
        is_int = np.equal(np.mod(x, 1), 0)
        return is_int

    def sparse_matrix_from_coo(self, coo):
        row = coo[:, 0]
        col = coo[:, 1]
        values = coo[:, 2]

        """Check if imaginary part of row and col is zero"""
        if np.all(np.isreal(row)) and np.all(np.isreal(col)):
            row = row.real
            col = col.real

            """Check if first and second column contain only integer entries"""
            if np.all(self.is_integer(row)) and np.all(self.is_integer(col)):

                """Convert row and col to int"""
                row = row.astype(int)
                col = col.astype(int)

                """Create coo-matrix"""
                A = scipy.sparse.coo_matrix((values, (row, col)))
                return A
            else:
                raise ValueError('coo contains non-integer entries for row and col.')
        else:
            raise ValueError('coo contains complex entries for row and col.')

    def setUp(self):
        self.filename_int = testpath + 'spmatrix_int_out.coo.dat'
        self.filename_float = testpath + 'spmatrix_float_out.coo.dat'
        self.filename_complex = testpath + 'spmatrix_complex_out.coo.dat'

        """Tri-diagonal test matrices"""
        dim = 10
        d0 = np.arange(0, dim)
        d1 = np.arange(dim, 2 * dim - 1)
        d_1 = np.arange(2 * dim, 3 * dim - 1)

        self.A_int = scipy.sparse.diags((d0, d1, d_1), (0, 1, -1), dtype=np.int).tocoo()
        self.A_float = scipy.sparse.diags((d0, d1, d_1), (0, 1, -1)).tocoo()
        self.A_complex = self.A_float + 1j * self.A_float

    def tearDown(self):
        os.remove(self.filename_int)
        os.remove(self.filename_float)
        os.remove(self.filename_complex)

    def test_write_matrix_sparse(self):
        write_matrix(self.filename_int, self.A_int, fmt='%d')
        coo_n = np.loadtxt(self.filename_int, dtype=np.int)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_int - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))

        write_matrix(self.filename_float, self.A_float)
        coo_n = np.loadtxt(self.filename_float, dtype=np.float)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_float - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))

        write_matrix(self.filename_complex, self.A_complex)
        coo_n = np.loadtxt(self.filename_complex, dtype=np.complex)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_complex - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))


################################################################################
# binary
################################################################################

################################################################################
# dense
################################################################################

class TestLoadMatrixDense(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'matrix_int.npy'
        self.filename_float = testpath + 'matrix_float.npy'
        self.filename_complex = testpath + 'matrix_complex.npy'

        self.A_int = np.load(self.filename_int)
        self.A_float = np.load(self.filename_float)
        self.A_complex = np.load(self.filename_complex)

    def tearDown(self):
        pass

    def test_load_matrix(self):
        A = load_matrix(self.filename_int)
        self.assertTrue(np.all(A == self.A_int))

        A = load_matrix(self.filename_float)
        self.assertTrue(np.all(A == self.A_float))

        A = load_matrix(self.filename_complex)
        self.assertTrue(np.all(A == self.A_complex))


class TestSaveMatrixDense(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'matrix_int_out.npy'
        self.filename_float = testpath + 'matrix_float_out.npy'
        self.filename_complex = testpath + 'matrix_complex_out.npy'

        self.A_int = np.arange(3 * 3).reshape(3, 3)
        self.A_float = 1.0 * self.A_int
        self.A_complex = np.arange(3 * 3).reshape(3, 3) + 1j * np.arange(9, 3 * 3 + 9).reshape(3, 3)

    def tearDown(self):
        os.remove(self.filename_int)
        os.remove(self.filename_float)
        os.remove(self.filename_complex)

    def test_write_matrix(self):
        save_matrix(self.filename_int, self.A_int)
        An = np.load(self.filename_int)
        self.assertTrue(np.all(An == self.A_int))

        save_matrix(self.filename_float, self.A_float)
        An = np.load(self.filename_int)
        self.assertTrue(np.all(An == self.A_float))

        save_matrix(self.filename_complex, self.A_complex)
        An = np.load(self.filename_complex)
        self.assertTrue(np.all(An == self.A_complex))


################################################################################
# sparse
################################################################################

class TestLoadMatrixSparse(unittest.TestCase):
    def setUp(self):
        self.filename_int = testpath + 'spmatrix_int.coo.npy'
        self.filename_float = testpath + 'spmatrix_float.coo.npy'
        self.filename_complex = testpath + 'spmatrix_complex.coo.npy'

        """Reference matrices in dense storage"""
        self.reference_int = testpath + 'spmatrix_int_reference.dat'
        self.reference_float = testpath + 'spmatrix_float_reference.dat'
        self.reference_complex = testpath + 'spmatrix_complex_reference.dat'

    def tearDown(self):
        pass

    def test_load_matrix(self):
        A = np.loadtxt(self.reference_int, dtype=np.int)
        A_n = load_matrix(self.filename_int).toarray()
        self.assertTrue(np.all(A == A_n))

        A = np.loadtxt(self.reference_float)
        A_n = load_matrix(self.filename_float).toarray()
        self.assertTrue(np.all(A == A_n))

        A = np.loadtxt(self.reference_complex, dtype=np.complex)
        A_n = load_matrix(self.filename_complex).toarray()
        self.assertTrue(np.all(A == A_n))


class TestSaveMatrixSparse(unittest.TestCase):
    def is_integer(self, x):
        """Check if elements of an array can be represented by integers.
        
        Parameters 
        ----------
        x : ndarray
            Array to check.
        
        Returns
        -------
        is_int : ndarray of bool
            is_int[i] is True if x[i] can be represented
            as int otherwise is_int[i] is False.
        
        """
        is_int = np.equal(np.mod(x, 1), 0)
        return is_int

    def sparse_matrix_from_coo(self, coo):
        row = coo[:, 0]
        col = coo[:, 1]
        values = coo[:, 2]

        """Check if imaginary part of row and col is zero"""
        if np.all(np.isreal(row)) and np.all(np.isreal(col)):
            row = row.real
            col = col.real

            """Check if first and second column contain only integer entries"""
            if np.all(self.is_integer(row)) and np.all(self.is_integer(col)):

                """Convert row and col to int"""
                row = row.astype(int)
                col = col.astype(int)

                """Create coo-matrix"""
                A = scipy.sparse.coo_matrix((values, (row, col)))
                return A
            else:
                raise ValueError('coo contains non-integer entries for row and col.')
        else:
            raise ValueError('coo contains complex entries for row and col.')

    def setUp(self):
        self.filename_int = testpath + 'spmatrix_int_out.coo.npy'
        self.filename_float = testpath + 'spmatrix_float_out.coo.npy'
        self.filename_complex = testpath + 'spmatrix_complex_out.coo.npy'

        """Tri-diagonal test matrices"""
        dim = 10
        d0 = np.arange(0, dim)
        d1 = np.arange(dim, 2 * dim - 1)
        d_1 = np.arange(2 * dim, 3 * dim - 1)

        self.A_int = scipy.sparse.diags((d0, d1, d_1), (0, 1, -1), dtype=np.int).tocoo()
        self.A_float = scipy.sparse.diags((d0, d1, d_1), (0, 1, -1)).tocoo()
        self.A_complex = self.A_float + 1j * self.A_float

    def tearDown(self):
        os.remove(self.filename_int)
        os.remove(self.filename_float)
        os.remove(self.filename_complex)

    def test_save_matrix(self):
        save_matrix(self.filename_int, self.A_int)
        coo_n = np.load(self.filename_int)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_int - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))

        save_matrix(self.filename_float, self.A_float)
        coo_n = np.load(self.filename_float)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_float - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))

        save_matrix(self.filename_complex, self.A_complex)
        coo_n = np.load(self.filename_complex)
        """Create sparse matrix from coo data"""
        A_n = self.sparse_matrix_from_coo(coo_n)
        diff = (self.A_complex - A_n).tocsr()
        """Check for empty array of non-zero entries"""
        self.assertTrue(np.all(diff.data == 0.0))


if __name__ == "__main__":
    unittest.main()
        