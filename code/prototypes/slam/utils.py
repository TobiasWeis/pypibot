import numpy as np
from scipy.spatial.distance import cdist

def best_fit_transform(A, B):
    '''
    Calculates the least-squares best-fit transform between corresponding 2D points A->B
    Input:
      A: Nx2 numpy array of corresponding 3D points
      B: Nx2 numpy array of corresponding 3D points
    Returns:
      T: 3x3 homogeneous transformation matrix
      R: 2x2 rotation matrix
      t: 2x1 column vector
    '''

    assert len(A) == len(B)

    # translate points to their centroids
    centroid_A = np.mean(A.astype(np.float64), axis=0)
    centroid_B = np.mean(B.astype(np.float64), axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
        print "===================================== IT HAPPENED!"
    #   Vt[2,:] *= -1
    #   R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    # homogeneous transformation
    T = np.identity(3)
    T[0:2, 0:2] = R
    T[0:2, 2] = t

    return T, R, t

def nearest_neighbor(src, dst):
    '''
    Find the nearest (Euclidean) neighbor in dst for each point in src
    Input:
        src: Nx3 array of points
        dst: Nx3 array of points
    Output:
        distances: Euclidean distances of the nearest neighbor
        indices: dst indices of the nearest neighbor
    '''
    all_dists = cdist(src, dst, 'euclidean')
    indices = all_dists.argmin(axis=1)
    distances = all_dists[np.arange(all_dists.shape[0]), indices]

    return distances, indices

def icp(A, B, init_pose=None, max_iterations=15, tolerance=0.01):
    '''
    The Iterative Closest Point method
    Input:
        A: Nx3 numpy array of source 3D points
        B: Nx3 numpy array of destination 3D point
        init_pose: 4x4 homogeneous transformation
        max_iterations: exit algorithm after max_iterations
        tolerance: convergence criteria
    Output:
        T: final homogeneous transformation
        distances: Euclidean distances (errors) of the nearest neighbor
    '''

    # make points homogeneous, copy them so as to maintain the originals
    src = np.ones((3,A.shape[0]))
    dst = np.ones((3,B.shape[0]))
    src[0:2,:] = np.copy(A.T)
    dst[0:2,:] = np.copy(B.T)

    # apply the initial pose estimation
    if init_pose is not None:
        src = np.dot(init_pose, src)

    prev_error = 0

    for i in range(max_iterations):
        print i,",",
        # find the nearest neighbours between the current source and destination points
        distances, indices = nearest_neighbor(src[0:2,:].T, dst[0:2,:].T)

        # compute the transformation between the current source and nearest destination points
        T,_,_ = best_fit_transform(src[0:2,:].T, dst[0:2,indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error
        mean_error = np.sum(distances) / distances.size
 
        if abs(prev_error - mean_error) < tolerance:
            break

        prev_error = mean_error

    # calculate final transformation
    # so we discard all transformations before?!
    T,_,_ = best_fit_transform(A, src[0:2,:].T)

    return T, distances
