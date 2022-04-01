from PIL import Image, ImageEnhance
import numpy


def find_coefficients(source_coords, target_coords):
    matrix = []
    for s, t in zip(source_coords, target_coords):
        matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0] * t[0], -s[0] * t[1]])
        matrix.append([0, 0, 0, t[0], t[1], 1, -s[1] * t[0], -s[1] * t[1]])
    A = numpy.matrix(matrix, dtype=float)
    B = numpy.array(source_coords).reshape(8)
    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


def image_manipulation(co_ords, scale_r, file_path):
    for vert in co_ords:
        vert[0] = int(scale_r * vert[0])
        vert[1] = int(scale_r * vert[1])

    least_x = min(co_ords[0][0], co_ords[3][0])
    least_y = min(co_ords[0][1], co_ords[1][1])

    coeffs = find_coefficients(co_ords, [[0, 0],
                                         [max(co_ords[1][0], co_ords[2][0]) - least_x, 0],
                                         [max(co_ords[1][0], co_ords[2][0]) - least_x,
                                          max(co_ords[2][1], co_ords[3][1]) - least_y],
                                         [0, max(co_ords[2][1], co_ords[3][1]) - least_y]])

    img = Image.open(file_path)
    img = img.transform((max(co_ords[1][0], co_ords[2][0]) - least_x, max(co_ords[2][1], co_ords[3][1]) - least_y),
                        Image.PERSPECTIVE,
                        coeffs,
                        Image.BICUBIC)
    # img.show()
    return img
