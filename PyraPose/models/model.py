import tensorflow.keras as keras
import tensorflow as tf
from .. import initializers
from .. import layers
from . import assert_training_model


def default_classification_model(
        num_classes,
        pyramid_feature_size=256,
        prior_probability=0.01,
        classification_feature_size=256,
):
    options = {
        'kernel_size': 3,
        'strides': 1,
        'padding': 'same',
        # 'kernel_regularizer': keras.regularizers.l2(0.001),
    }

    if keras.backend.image_data_format() == 'channels_first':
        inputs = keras.layers.Input(shape=(pyramid_feature_size, None, None))
    else:
        inputs = keras.layers.Input(shape=(None, None, pyramid_feature_size))

    outputs = inputs
    for i in range(4):
        outputs = keras.layers.Conv2D(
            filters=classification_feature_size,
            activation='relu',
            kernel_initializer=keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
            bias_initializer='zeros',
            **options
        )(outputs)

    labels = keras.layers.Conv2D(
        filters=num_classes,
        kernel_initializer=keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
        bias_initializer=initializers.PriorProbability(probability=prior_probability),
        **options
    )(outputs)

    # reshape output and apply sigmoid
    if keras.backend.image_data_format() == 'channels_first':
        labels = keras.layers.Permute((2, 3, 1))(labels)
    labels = keras.layers.Reshape((-1, num_classes))(labels)
    labels = keras.layers.Activation('sigmoid')(labels)

    # cent = keras.layers.Conv2D(
    #    filters=1,
    #    kernel_initializer=keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
    #    bias_initializer=initializers.PriorProbability(probability=prior_probability),
    #    **options
    # )(outputs)

    # reshape output and apply sigmoid
    # if keras.backend.image_data_format() == 'channels_first':
    #    cent = keras.layers.Permute((2, 3, 1))(cent)
    # cent = keras.layers.Reshape((-1, 1))(cent) # centerness = keras.layers.Reshape((-1, num_classes))(centerness)
    # cent = keras.layers.Activation('sigmoid')(cent)

    return keras.models.Model(inputs=inputs, outputs=labels)  # , keras.models.Model(inputs=inputs, outputs=cent)


def default_boxes_model(num_values, pyramid_feature_size=256, prior_probability=0.01, regression_feature_size=256):
    options = {
        'kernel_size': 3,
        'strides': 1,
        'padding': 'same',
        'kernel_initializer': keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
        'bias_initializer': 'zeros',
        # 'kernel_regularizer' : keras.regularizers.l2(0.001),
    }

    if keras.backend.image_data_format() == 'channels_first':
        inputs = keras.layers.Input(shape=(pyramid_feature_size, None, None))
    else:
        inputs = keras.layers.Input(shape=(None, None, pyramid_feature_size))

    outputs = inputs
    for i in range(4):
        outputs = keras.layers.Conv2D(
            filters=regression_feature_size,
            activation='relu',
            **options
        )(outputs)

    regress = keras.layers.Conv2D(num_values, **options)(outputs)
    # regress = keras.layers.SeparableConv2D(num_values, **options)(outputs)
    if keras.backend.image_data_format() == 'channels_first':
        regress = keras.layers.Permute((2, 3, 1))(regress)
    regress = keras.layers.Reshape((-1, num_values))(regress)

    return keras.models.Model(inputs=inputs, outputs=regress)


def default_regression_model(num_values, pyramid_feature_size=256, prior_probability=0.01, regression_feature_size=512):
    options = {
        'kernel_size': 3,
        'strides': 1,
        'padding': 'same',
        'kernel_initializer': keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
        'bias_initializer': 'zeros',
        'kernel_regularizer': keras.regularizers.l2(0.001),
        # 'pointwise_regularizer': keras.regularizers.l2(0.001),
        # 'depthwise_regularizer': keras.regularizers.l2(0.001),
    }

    options_centerness = {
        'kernel_size': 3,
        'strides': 1,
        'padding': 'same',
    }

    if keras.backend.image_data_format() == 'channels_first':
        inputs = keras.layers.Input(shape=(pyramid_feature_size, None, None))
    else:
        inputs = keras.layers.Input(shape=(None, None, pyramid_feature_size))

    outputs = inputs
    for i in range(4):
        outputs = keras.layers.Conv2D(
            filters=regression_feature_size,
            activation='relu',
            **options
        )(outputs)

    regress = keras.layers.Conv2D(num_values, **options)(outputs)
    # regress = keras.layers.SeparableConv2D(num_values, **options)(outputs)
    if keras.backend.image_data_format() == 'channels_first':
        regress = keras.layers.Permute((2, 3, 1))(regress)
    regress = keras.layers.Reshape((-1, num_values))(regress)

    # conf = keras.layers.Conv2D(
    #    filters=num_values,
    #    kernel_initializer=keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
    #    bias_initializer=initializers.PriorProbability(probability=prior_probability),
    #    **options_centerness
    # )(outputs)

    # reshape output and apply sigmoid
    # if keras.backend.image_data_format() == 'channels_first':
    #    conf = keras.layers.Permute((2, 3, 1))(conf)
    # conf = keras.layers.Reshape((-1, num_values))(conf) # centerness = keras.layers.Reshape((-1, num_classes))(centerness)
    # conf = keras.layers.Activation('sigmoid')(conf)

    # return keras.models.Model(inputs=inputs, outputs=regress)
    return keras.models.Model(inputs=inputs, outputs=regress)  # , keras.models.Model(inputs=inputs, outputs=conf)


def default_pose_model(num_classes, prior_probability=0.01, regression_feature_size=512):
    options = {
        'kernel_size': 3,
        'strides': 1,
        'padding': 'same',
        'kernel_initializer': keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
        'bias_initializer': 'zeros',
        'kernel_regularizer': keras.regularizers.l2(0.001),
    }

    if keras.backend.image_data_format() == 'channels_first':
        inputs = keras.layers.Input(shape=(16, num_classes, None))
    else:
        inputs = keras.layers.Input(shape=(None, num_classes, 16))

    outputs = inputs

    translations = []
    rotations = []
    for i in range(num_classes):
        out_cls = outputs[:, :, i, :]
        out_cls = keras.layers.Conv1D(filters=128, activation='relu', **options)(out_cls)
        out_cls = keras.layers.Conv1D(filters=64, activation='relu', **options)(out_cls)

        translation = keras.layers.Conv1D(3, **options)(out_cls)
        if keras.backend.image_data_format() == 'channels_first':
            translation = keras.layers.Permute((2, 3, 1))(translation)
        translation = keras.layers.Reshape((-1, 1, 3))(translation)

        #depth = keras.layers.Conv1D(1, **options)(out_cls)
        #if keras.backend.image_data_format() == 'channels_first':
        #    translation = keras.layers.Permute((2, 3, 1))(depth)
        #depth = keras.layers.Reshape((-1, 1, 1))(depth)

        rotation = keras.layers.Conv1D(6, **options)(out_cls)
        if keras.backend.image_data_format() == 'channels_first':
            rotation = keras.layers.Permute((2, 3, 1))(rotation)
        rotation = keras.layers.Reshape((-1, 1, 6))(rotation)
        #rotation = tf.math.l2_normalize(rotation, axis=3)

        translations.append(translation)
        #depths.append(depth)
        rotations.append(rotation)
    translations = tf.concat(translations, axis=2)
    #depths = tf.concat(depths, axis=2)
    rotations = tf.concat(rotations, axis=2)
    rotations_1, rotations_2 = tf.split(rotations, num_or_size_splits=2, axis=3)
    rotations_1 = tf.math.l2_normalize(rotations_1, axis=3)
    rotations_2 = tf.math.l2_normalize(rotations_2, axis=3)
    rotations = tf.concat([rotations_1, rotations_2], axis=3)

    '''
    outputs = keras.layers.Reshape((-1, num_classes * 16))(outputs)
    outputs = keras.layers.Conv1D(filters=512, activation='relu', **options)(outputs)
    outputs = keras.layers.Conv1D(filters=256, activation='relu', **options)(outputs)

    translation = keras.layers.Conv1D(num_classes * 3, **options)(outputs)
    if keras.backend.image_data_format() == 'channels_first':
        translation = keras.layers.Permute((2, 3, 1))(translation)
    translation = keras.layers.Reshape((-1, num_classes, 3))(translation)

    rotation = keras.layers.Conv1D(num_classes * 4, **options)(outputs)
    if keras.backend.image_data_format() == 'channels_first':
        rotation = keras.layers.Permute((2, 3, 1))(rotation)
    rotation = keras.layers.Reshape((-1, num_classes, 4))(rotation)
    rotation = tf.math.l2_normalize(rotation, axis=3)
    '''

    #regress = tf.concat([translations, rotations], axis=3)

    return keras.models.Model(inputs=inputs, outputs=rotations, name='rotations'), keras.models.Model(inputs=inputs, outputs=translations, name='translations')


def default_confidence_model(num_classes):
    options = {
        'kernel_size': 1,
        'strides': 1,
        'padding': 'same',
        'kernel_initializer': keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None),
        'bias_initializer': 'zeros',
        'kernel_regularizer': keras.regularizers.l2(0.001),
    }

    if keras.backend.image_data_format() == 'channels_first':
        inputs = keras.layers.Input(shape=(num_classes*9, None, None))
        #inputs = keras.layers.Input(shape=(num_classes * (16 + 7), None))
    else:
        inputs = keras.layers.Input(shape=(None, None, num_classes*9))
        #inputs = keras.layers.Input(shape=(None, num_classes * (16 + 7)))

    outputs = inputs

    outputs = keras.layers.Conv2D(filters=256, activation='relu', **options)(outputs)
    outputs = keras.layers.Conv2D(filters=128, activation='relu', **options)(outputs)
    outputs = keras.layers.Conv2D(filters=num_classes, **options)(outputs)
    confidence = keras.layers.Activation('sigmoid')(outputs)

    conf_out = tf.concat([inputs, confidence], axis=3)
    conf_out = keras.layers.Reshape((-1, num_classes*10))(conf_out)

    return keras.models.Model(inputs=inputs, outputs=conf_out, name='confidences')


def __create_PFPN(C3, C4, C5, feature_size=256):
    options = {
        # 'kernel_regularizer': keras.regularizers.l2(0.001),
    }

    # 3x3 conv for test 4
    P3 = keras.layers.Conv2D(feature_size, kernel_size=1, strides=1, padding='same', **options)(C3)
    P4 = keras.layers.Conv2D(feature_size, kernel_size=1, strides=1, padding='same', **options)(C4)
    P5 = keras.layers.Conv2D(feature_size, kernel_size=1, strides=1, padding='same', **options)(C5)

    P5_upsampled = layers.UpsampleLike()([P5, P4])
    P4_upsampled = layers.UpsampleLike()([P4, P3])
    P4_mid = keras.layers.Add()([P5_upsampled, P4])
    P4_mid = keras.layers.Conv2D(feature_size, kernel_size=3, strides=1, activation='linear', padding='same',
                                 **options)(P4_mid)
    P3_mid = keras.layers.Add()([P4_upsampled, P3])
    P3_mid = keras.layers.Conv2D(feature_size, kernel_size=3, strides=1, activation='linear', padding='same',
                                 **options)(P3_mid)
    P3_down = keras.layers.Conv2D(feature_size, kernel_size=3, strides=2, activation='linear', padding='same',
                                  **options)(P3_mid)
    P3_fin = keras.layers.Add()([P3_mid, P3])  # skip connection
    P3 = keras.layers.Conv2D(feature_size, kernel_size=3, strides=1, activation='linear', padding='same', name='P3',
                             **options)(P3_fin)

    P4_fin = keras.layers.Add()([P3_down, P4_mid])
    P4_down = keras.layers.Conv2D(feature_size, kernel_size=3, strides=2, activation='linear', padding='same',
                                  **options)(P4_mid)
    P4_fin = keras.layers.Add()([P4_fin, P4])  # skip connection
    P4 = keras.layers.Conv2D(feature_size, kernel_size=3, strides=1, activation='linear', padding='same', name='P4',
                             **options)(P4_fin)
    P5_fin = keras.layers.Add()([P4_down, P5])
    P5 = keras.layers.Conv2D(feature_size, kernel_size=3, strides=1, activation='linear', padding='same', name='P5',
                             **options)(P5_fin)

    return [P3, P4, P5]


def pyrapose(
        inputs,
        backbone_layers,
        num_classes,
        obj_correspondences=None,
        obj_diameters=None,
        intrinsics=None,
        create_pyramid_features=__create_PFPN,
        name='pyrapose'
):
    regression_branch = default_regression_model(16)
    pose_branch = default_pose_model(num_classes)
    # boxes_branch = default_regression_model(4)
    location_branch = default_classification_model(num_classes)
    confidence_branch = default_confidence_model(num_classes)

    b1, b2, b3 = backbone_layers
    P3, P4, P5 = create_pyramid_features(b1, b2, b3)

    pyramids = []
    regression_P3 = regression_branch(P3)
    regression_P4 = regression_branch(P4)
    regression_P5 = regression_branch(P5)
    regression = keras.layers.Concatenate(axis=1, name='points')([regression_P3, regression_P4, regression_P5])
    pyramids.append(regression)

    location_P3 = location_branch(P3)
    location_P4 = location_branch(P4)
    location_P5 = location_branch(P5)
    pyramids.append(keras.layers.Concatenate(axis=1, name='cls')([location_P3, location_P4, location_P5]))

    location_coordinates = layers.Locations_Hacked(name='denorm_locations')(P3)
    locations_tiled = tf.tile(tf.expand_dims(location_coordinates, axis=2, name='locations_expanded'),
                              [1, 1, num_classes, 1])
    rep_object_diameters = tf.tile(obj_diameters[tf.newaxis, tf.newaxis, :, tf.newaxis], [1, 6300, 1, 16])

    regression_tiled = tf.tile(tf.expand_dims(regression, axis=2, name='regression_expanded'), [1, 1, num_classes, 1],
                               name='regression_tiled')
    regression_tiled = regression_tiled * rep_object_diameters

    destd_boxes = layers.DenormRegression(name='DenormRegression')([regression_tiled, locations_tiled])

    location = pose_branch[1](destd_boxes)
    rotation = pose_branch[0](destd_boxes)
    pyramids.append(location)
    pyramids.append(rotation)

    # transform box with pose
    poses = tf.concat([location, rotation], axis=3)
    #rep_object_correspondences = tf.tile(obj_correspondences[tf.newaxis, tf.newaxis, :, :, :], [tf.shape(poses)[0], 6300, 1, 1, 1])
    #rep_intrinsics = tf.tile(intrinsics[tf.newaxis, tf.newaxis, :], [1, 6300, 1])
    #correspondences = tf.keras.backend.constant(obj_correspondences)
    #intrinsics_tensor = tf.keras.backend.constant(intrinsics)
    #projected_poses = layers.ProjectBoxes(name='ProjectBoxes')([poses, correspondences, intrinsics_tensor])
    
    #obj_correspondences = tf.tile(obj_correspondences, [1, 1, 1])
    #intriniscs = tf.tile(intrinsics, [1])

    x = location[:, :, :, 0] * 500.0
    y = location[:, :, :, 1] * 500.0
    z = ((location[:, :, :, 2] * (1 / 3)) + 1.0) * 1000.0
    trans = tf.stack([x, y, z], axis=3)
    trans = tf.tile(trans[:, :, :, tf.newaxis, :], [1, 1, 1, 8, 1])

    r1 = rotation[:, :, :, :3]
    r2 = rotation[:, :, :, 3:]
    r3 = tf.linalg.cross(r1, r2)
    r3 = tf.math.l2_normalize(r3, axis=3)
    rot = tf.stack([r1, r2, r3], axis=4)

    #box3d = tf.einsum('blcij,ckj->blcki', rot, obj_correspondences)
    #rep_obj_correspondences = tf.tile(obj_correspondences[tf.newaxis, tf.newaxis, :, :, :], [tf.shape(location)[0], tf.shape(location)[1], 1, 1, 1])
    rep_obj_correspondences = tf.tile(obj_correspondences[tf.newaxis, tf.newaxis, :, :, :], [tf.shape(location)[0], tf.shape(location)[1], 1, 1, 1])
    box3d = tf.linalg.matmul(rot, rep_obj_correspondences, transpose_a=False, transpose_b=True)
    box3d = tf.transpose(box3d, perm=[0, 1, 2, 4, 3])
    
    #td_test = tf.linalg.matmul(rot, rep_obj_correspondences, transpose_a=True, transpose_b=True)
    #tf.print('box3d: ', box3d)
    #tf.print('td_test: ', td_test)
    box3d = tf.math.add(box3d, trans)

    projected_boxes_x = box3d[:, :, :, :, 0] * intrinsics[0]
    projected_boxes_x = tf.math.divide_no_nan(projected_boxes_x, box3d[:, :, :, :, 2])
    projected_boxes_x = tf.math.add(projected_boxes_x, intrinsics[2])
    projected_boxes_y = box3d[:, :, :, :, 1] * intrinsics[1]
    projected_boxes_y = tf.math.divide_no_nan(projected_boxes_y, box3d[:, :, :, :, 2])
    projected_boxes_y = tf.math.add(projected_boxes_y, intrinsics[3])
    pro_boxes = tf.stack([projected_boxes_x, projected_boxes_y], axis=4)
    pro_boxes = tf.reshape(pro_boxes, shape=[tf.shape(location)[0], tf.shape(location)[1], tf.shape(location)[2], 16])
    
    
    discrepancy = tf.concat([destd_boxes, pro_boxes], axis=3)
    #discrepancy = tf.math.subtract(destd_boxes, projected_poses)

    rename_layer = keras.layers.Lambda(lambda x: x, name='reprojection')
    reprojection = rename_layer(discrepancy)
    pyramids.append(reprojection)
    # project box

    #confidence from reprojection
    #rename_layer = keras.layers.Lambda(lambda x: x, name='confidence')
    #confidences = rename_layer(discrepancy)
    #poses_conditioned_on_boxes = tf.concat([regression_tiled, location, rotation], axis=3)
    #pyramids.append(confidences)

    # confidence regression
    P3_poses = tf.reshape(poses[:, :4800, :, :], [-1, 60, 80, num_classes*9])
    P4_poses = tf.reshape(poses[:, 4800:6000, :, :], [-1, 30, 40, num_classes*9])
    P5_poses = tf.reshape(poses[:, 6000:, :, :], [-1, 15, 20, num_classes*9])
    P3_confs = confidence_branch(P3_poses)
    P4_confs = confidence_branch(P4_poses)
    P5_confs = confidence_branch(P5_poses)
    confidences = tf.concat([P3_confs, P4_confs, P5_confs], axis=1)
    rename_conf = keras.layers.Lambda(lambda x: x, name='confidence')
    confidences = rename_conf(confidences)
    pyramids.append(confidences)
    #P3_flat = tf.reshape(P3, [-1, 4800, 256])
    #P4_flat = tf.reshape(P4, [-1, 1200, 256])
    #P5_flat = tf.reshape(P5, [-1, 300, 256])
    #features_reshaped = tf.concat([P3_flat, P4_flat, P5_flat], axis=1)
    #poses = tf.concat([location, rotation], axis=3)
    #poses_over_classes = tf.reshape(poses, [-1, 6300, num_classes*9])
    #poses_conditioned_to_features = tf.concat([features_reshaped, poses_over_classes], axis=2)
    #confidences = confidence_branch(poses_conditioned_to_features)
    #pyramids.append(confidences)

    # confidence regression + pose conditioning
    #poses_conditioned_on_boxes = tf.concat([regression_tiled, location, rotation], axis=3)
    #print('poses_conditioned_on_boxes: ', poses_conditioned_on_boxes)
    #poses_conditioned_on_boxes = tf.reshape(poses_conditioned_on_boxes, [-1, 6300, num_classes * (16 + 7)])
    #confidences = confidence_branch(poses_conditioned_on_boxes)
    #pyramids.append(confidences)

    return keras.models.Model(inputs=inputs, outputs=pyramids, name=name)


def __build_locations(features, strides):
    locations = [
        layers.Locations(stride=strides[i], name='locations_{}'.format(i))(f) for i, f in enumerate(features)
    ]

    return keras.layers.Concatenate(axis=1, name='locations')(locations)


#def __build_destd(features, strides):
#    locations = [
#        layers.Locations(stride=strides[i], name='denorm_locations_{}'.format(i))(f) for i, f in enumerate(features)
#    ]

#    return keras.layers.Concatenate(axis=1, name='denorm_locations')(locations)


def inference_model(
        model=None,
        correspondences=None,
        object_diameters=None,
        num_classes=None,
        name='pyrapose',
        score_threshold=0.5,
        max_detections=300,
        **kwargs
):
    # create RetinaNet model
    if model is None:
        model = pyrapose(**kwargs)
    else:
        assert_training_model(model)

    # compute the anchors
    features = [model.get_layer(p_name).output for p_name in ['P3', 'P4', 'P5']]
    strides = [8, 16, 32]
    # features = [model.get_layer(p_name).output for p_name in ['P3_con', 'P3_sub', 'P4_con', 'P4_sub', 'P5_con']]
    locations = __build_locations(features, strides)

    regression = model.outputs[0]
    # residuals = model.outputs[1][:, :, 18:]
    classification = model.outputs[1]
    #poses = model.outputs[2]
    translations = model.outputs[2]
    rotations = model.outputs[3]
    consistency = model.outputs[4]
    cons1, cons2 = tf.split(consistency, num_or_size_splits=2, axis=3)
    consistency = tf.math.reduce_euclidean_norm(cons1 - cons2, axis=3)
    print('consistency: ', consistency)

    #confidences = model.outputs[4]
    #_, confidences = tf.split(confidences, num_or_size_splits=[-1, num_classes], axis=2)

    detections = layers.FilterDetections(
        name='filtered_detections',
        score_threshold=score_threshold,
        max_detections=max_detections,
    #)([regression, classification, locations, translations, rotations, confidences])
    )([regression, classification, locations, translations, rotations, consistency])

    tf_diameter = tf.convert_to_tensor(object_diameters)
    rep_object_diameters = tf.gather(tf_diameter, indices=detections[3])

    poses = tf.concat([detections[4], detections[5]], axis=3)
    poses = layers.DenormPoses(name='poses_world')(poses)
    boxes3D = layers.RegressBoxes3D(name='boxes3D')([detections[0], detections[1], rep_object_diameters])

    # construct the model
    # return keras.models.Model(inputs=model.inputs, outputs=[boxes3D, classification], name=name)
    # return keras.models.Model(inputs=model.inputs, outputs=[regression, classification], name=name)
    #return keras.models.Model(inputs=model.inputs, outputs=[boxes3D, detections[2], detections[3], poses, detections[6]], name=name)
    return keras.models.Model(inputs=model.inputs,
                              outputs=[boxes3D, detections[2], detections[3], poses, detections[6]], name=name)
