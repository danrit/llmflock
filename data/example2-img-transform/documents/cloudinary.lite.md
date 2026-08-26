The Transformation URL API enables you to deliver media assets, including a large variety of on-the-fly transformations through the use of URL parameters. This reference provides comprehensive coverage of all available URL transformation parameters, including syntax, value details, and examples.

> See also:
>
> - [Image transformation guide](image_transformations)
> - [Video transformation guide](video_manipulation_and_delivery)
> - [Transformation basics video tutorial](transformation_basics_tutorial)

### Overview

The default Cloudinary asset delivery URL has the following structure:

https://res.cloudinary.com/<cloud_name>/<asset_type>/<delivery_type>/<transformations>/<version>/<public_id_full_path>.<extension>

This reference covers the parameters and corresponding options and values that can be used in the `<transformations>` element of the URL. It also covers the [&lt;extension&gt;](#extension) element.

For information on other elements of the URL, see [Transformation URL syntax](image_transformations#transformation_url_syntax).

> Important
>
> The transformation names and syntax shown in this reference refer to the **URL API**.
>
>
> Depending on the Cloudinary SDK you use, the names and syntax for the same transformation may be different. Therefore, all of the transformation examples in this reference also include the code for generating the example delivery URL from your chosen SDK.
>
>
> The SDKs additionally provide a variety of helper methods to simplify the building of the transformation URL as well as other built-in capabilities. You can find more information about these in the relevant [SDK guides](cloudinary_sdks).

> Tip
> You can use the [Media Library](media_library_for_developers) to preview and manage your transformations:
>
> - [Quickly test transformations](media_library_for_developers#quick_delivery_testing) in the Media Library by opening the image URL and manually adding transformations before implementing them programmatically.
> - [Manage derived assets](media_library_for_developers#derived_assets) from the **Derived Assets** tab in an asset's Manage page.

##### Parameter types

There are two types of transformation parameters:

- **Action parameters**: Parameters that perform a specific transformation on the asset.
- **Qualifier parameters**: Parameters that do not perform an action on their own, but rather alter the default behavior or otherwise adjust the outcome of the corresponding action parameter.

See the *Transformation Guide* for additional guidelines and best practices regarding [parameter types](image_transformations#parameter_types).

### .&lt;extension&gt;


Although not a transformation parameter belonging to the `<transformation>` element of the URL, the extension of the URL can transform the format of the delivered asset, in the same way as [f_&lt;supported format&gt;](#supported-format).

If [f_&lt;supported format&gt;](#supported-format) or [f_&lt;auto&gt;](#auto-3) are not specified in the URL, the format is determined by the extension. If no format or extension is specified, then the asset is delivered in its originally uploaded format.

- If using an SDK to generate your URL, you can control the extension using the `format` parameter, or by adding the extension to the public ID.
- If using a raw transformation, for example to define an [eager](eager_and_incoming_transformations#eager_transformations) or [named](named_transformations) transformation, you can specify the extension at the end of the transformation parameters, following a forward slash. For example, `c_pad,h_300,w_300/jpg` means that the delivery URL has transformation parameters of `c_pad,h_300,w_300` and a `.jpg` extension. `c_pad,h_300,w_300/` represents the same transformation parameters, but with no extension.

> Note
> As the extension is considered to be part of the transformation, be careful when defining [eager transformations](eager_and_incoming_transformations#eager_transformations) and transformations that are allowed when [strict transformations](control_access_to_media#strict_transformations) are enabled, as the delivery URL must exactly match the transformation, including the extension.

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| extension | string | The format to use when delivering the asset.  **Possible values**: Any supported delivery format as relevant for the file type you are delivering:  - [Supported image formats](image_format_support#supported_image_formats) - [Supported video formats](video_transcoding#supported_video_formats) - [Supported audio formats](audio_transformations#supported_audio_formats)  **Default**: The originally uploaded format of the asset. |

##### Examples

1. Deliver the image as a JPEG by setting the extension (`.jpg`):

  ```
  https://res.cloudinary.com/demo/image/upload/sheep.jpg
  ```
2. Deliver the image as a PNG by using the SDK `format` parameter, which sets the extension of the URL. Note that in contrast to [f (fetch format)](#f-format), this isn't a *transformation* parameter, but rather an SDK parameter that controls the file extension of the public ID in the resulting URL.

  ```
  https://res.cloudinary.com/demo/image/upload/sheep.png
  ```
3. Deliver the image in its originally uploaded format (no extension specified):

  ```
  https://res.cloudinary.com/demo/image/upload/sheep
  ```

### a (angle)


Rotates or flips an asset by the specified number of degrees or automatically according to its orientation or available metadata. Multiple modes can be applied by [concatenating their values with a dot](#dot_rotation).

**Learn more**: [Rotating images](effects_and_artistic_enhancements#rotating_images) | [Rotating videos](video_manipulation_and_delivery#rotating_videos)

#### &lt;degrees&gt;

 `a_<degrees>`
Rotates an asset by the specified angle.

**See also**: [Arithmetic expressions](user_defined_variables#arithmetic_expressions)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| degrees | integer | The number of degrees to rotate the asset clockwise (positive value) or counter-clockwise (negative value). If the angle is not a multiple of 90, a rectangular bounding box is added containing the rotated asset. |

> Note
> If either the width or height of an asset exceeds 3000 pixels, the asset is automatically downscaled first, and then rotated. This applies to the size of the asset that is the input to the rotation, whether that be the output of a previous chained transformation or the original asset size.

##### Examples

1. Rotate an image by 90 degrees clockwise (`a_90`):

  ```
  https://res.cloudinary.com/demo/image/upload/a_90/sheep.jpg
  ```
2. Rotate a video by 20 degrees counterclockwise (`a_-20`):

  ```
  https://res.cloudinary.com/demo/video/upload/a_-20/docs/hotel-slow-motion-waterfall.mp4
  ```

#### &lt;mode&gt;

 `a_<mode>`
Rotates an image or video based on the specified mode.

**Use with:** To apply one of the `a_auto` modes, use it as a qualifier with a [cropping](#c-cropresize) action that adjusts the aspect ratio, as per the syntax details and example below.

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| mode | constant | **Required.** The rotation mode to apply. **Possible values**:  - `vflip`: Vertically mirror flips the image or video. - `hflip`: Horizontally mirror flips the image or video. - `ignore`:  **Applicable to images only**. By default, the image is automatically rotated according to the EXIF data stored by the camera when the image was taken. Set the rotation to `ignore` if you do not want the image to be automatically rotated. - `auto_right`: **Applicable to images only**. If the requested aspect ratio of a crop does not match the image's original aspect ratio (landscape vs portrait ratio), rotates the image 90 degrees clockwise. Must be used as a [qualifier](#parameter-types) of a [cropping](#c-cropresize) action. - `auto_left`: **Applicable to images only**. If the requested aspect ratio of a crop does not match the image's original aspect ratio (it is greater than 1, while the original is less than 1, or vice versa), rotates the image 90 degrees counterclockwise. Must be used as a [qualifier](#parameter-types) of a [cropping](#c-cropresize) action. |

> Tip
> To apply multiple values, separate each value with a dot (`.`). For example to horizontally flip the image and rotate it by 45 degrees: `a_hflip.45`

##### Examples

1. Vertically mirror flip the image and then rotate it by another 20 degrees clockwise using the dot notation to apply more than one rotation option (`a_vflip`):

  ```
  https://res.cloudinary.com/demo/image/upload/a_vflip.20/sheep.png
  ```
2. In the following example, the image is rotated counter-clockwise (`a_auto_left`) because the original image was a landscape (aspect ratio greater than 1), while the requested aspect ratio is portrait (aspect ratio = 0.7).
  If the requested aspect ratio had been 1.0 or larger, the same transformation would not result in rotation.

  ```
  https://res.cloudinary.com/demo/image/upload/c_fill,w_300,ar_0.7,a_auto_left/sheep.jpg
  ```

  <a id="dot_rotation"></a>

### c (crop/resize)


Changes the size of the delivered asset according to the requested width & height dimensions.

Depending on the selected `<crop mode>`, parts of the original asset may be cropped out and/or the asset may be resized (scaled up or down).

When using any of the modes that can potentially crop parts of the asset, the selected [gravity](#g-gravity) parameter controls which part of the original asset is kept in the resulting delivered file.

**Learn more**: [Resizing and cropping images](resizing_and_cropping) | [Resizing and cropping videos](video_resizing_and_cropping)

#### auto

 `c_auto`
Automatically determines the best crop based on the gravity and specified dimensions.

If the requested dimensions are smaller than the best crop, the result is downscaled. If the requested dimensions are larger than the original image, the result is upscaled. Use this mode in conjunction with the [g (gravity)](#g-gravity) parameter.

##### Required qualifiers

[g (gravity)](#g-gravity)

And

Two of the following: [w (width)](#w-width) | [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio)

(In rare cases, you may choose to [provide only one sizing qualifier](resizing_and_cropping#one_resize_qualifier))

**Learn more**: [Automatic gravity with the automatic cropping mode](image_automatic_gravity#automatic_gravity_with_the_auto_cropping_mode)

##### Example

Create a 16:9 aspect ratio crop of an image of two smiling ladies, automatically deciding which parts of the image to keep (`c_auto,g_auto,ar_16:9,h_150`):

```
https://res.cloudinary.com/demo/image/upload/c_auto,g_auto,ar_16:9,h_150/docs/ladies-smiling.jpg
```

#### fill

 `c_fill`
Creates an asset with the exact specified width and height without distorting the asset. This option first scales as much as needed to at least fill both of the specified dimensions. If the requested aspect ratio is different than the original, cropping will occur on the dimension that exceeds the requested size after scaling. You can specify which part of the original asset you want to keep if cropping occurs using the [gravity](#g-gravity) (set to 'center' by default).

##### Required qualifiers

At least one of the following: [w (width)](#w-width) | [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio)

(In rare cases, you may choose to [provide only one sizing qualifier](resizing_and_cropping#one_resize_qualifier))

##### Optional qualifiers

[g (gravity)](#g-gravity)

##### Examples

1. Fill to a width and height of 150 pixels (`c_fill,h_150,w_150`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_fill,h_150,w_150/docs/camera-640.jpg
  ```
2. Fill to a width and height of 150 pixels with east gravity (`c_fill,g_east,h_150,w_150`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_fill,g_east,h_150,w_150/docs/camera-640.jpg
  ```

#### fit

 `c_fit`
Scales the asset up or down so that it takes up as much space as possible within a bounding box defined by the specified dimension parameters without cropping any of it. The original aspect ratio is retained and all of the original image is visible.

##### Required qualifiers

Two of the following: [w (width)](#w-width) | [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio)

(In rare cases, you may choose to [provide only one sizing qualifier](resizing_and_cropping#one_resize_qualifier))

##### Example

Fit an image within a width and height of 150 pixels (`c_fit,h_150,w_150`).

```
https://res.cloudinary.com/demo/image/upload/c_fit,h_150,w_150/docs/camera-640.jpg
```

#### pad

 `c_pad`
Resizes the asset to fill the specified width and height while retaining the original aspect ratio (by default) and with all of the original asset visible. If the proportions of the original asset do not match the specified width and height, padding is added to the asset to reach the required size. You can also specify where the original asset is placed using the [gravity](#g-gravity) parameter (set to `center` by default). Additionally, you can specify the color of the [background](#b-background) in the case that padding is added.

If you're looking to apply padding to all sides of an asset, consider using [c_lpad](#lpad) or [c_mpad](#mpad).

##### Required qualifiers

Two of the following: [w (width)](#w-width) | [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio)

(In rare cases, you may choose to [provide only one sizing qualifier](resizing_and_cropping#one_resize_qualifier)). See also the [padding notes](#padding_notes) below.

##### Optional qualifiers

[g_&lt;gravity position&gt;](#compass-position) | [b (background)](#b-background)

<a id="padding_notes"></a>

> Padding notes
>
> - **Two sizing qualifiers recommended for pad resizing:** `c_pad` (as well as `c_lpad`, and `c_mpad`) work best when you provide two of `w`, `h`, or `ar`. If you provide only one (for example, just `w`), Cloudinary derives the other dimension from the original aspect ratio. Depending on the requested canvas, this can result in padding on both axes.
> - **Width-only (horizontal) padding:** If you want to add padding only to the width (not height):
>
>
>   - **Preferred:** Specify both `w` and `h` (for example, set `h` equal to the original height or to the desired canvas height), e.g.:
>     `.../image/upload/c_lpad,h_300,w_450/...jpg`
>   - **Alternative:** Add the `fl_ignore_aspect_ratio` flag to change only one dimension, then pad. For example:
>     `.../image/upload/c_lpad,fl_ignore_aspect_ratio,w_450/...jpg`
>     This keeps the original height while setting the width to 450, so padding is added horizontally only. (See also: [fl_ignore_aspect_ratio](#ignore_aspect_ratio)).
> - **Avoiding scale-down:** If you want to preserve the original size and still add padding to a requested canvas, use `c_mpad` (minimum pad). For example:
>   `.../image/upload/c_mpad,h_120,w_160/...jpg`
>   When the original is larger than the requested size, `c_mpad` delivers the original and adds padding as needed.

##### Example

Pad an image with a black background to a width and height of 150 pixels (`b_black,c_pad,h_150,w_150`):

```
https://res.cloudinary.com/demo/image/upload/b_black,c_pad,h_150,w_150/docs/camera-640.jpg
```

#### thumb

 `c_thumb`
Creates image thumbnails based on a gravity position. Must always be accompanied by the [g (gravity)](#g-gravity) parameter. This cropping mode generates a thumbnail of an image with the exact specified width and height dimensions and with the original proportions retained, but the resulting image might be scaled to fit in the specified dimensions. You can specify the [z (zoom)](#z-zoom) parameter to determine how much to scale the resulting image within the specified width and height.

##### Required qualifiers

[g (gravity)](#g-gravity)

And

Two of the following: [w (width)](#w-width) | [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio)

(In rare cases, you may choose to [provide only one sizing qualifier](resizing_and_cropping#one_resize_qualifier))

##### Optional qualifiers

[z (zoom)](#z-zoom)

##### Example

Crop an image to a 150x150 thumbnail using face detection (`c_thumb,g_face,h_150,w_150`):

```
https://res.cloudinary.com/demo/image/upload/c_thumb,g_face,h_150,w_150/woman.jpg
```

### e (effect)


Applies the specified effect to an asset.

> Note
>
> If you specify more than one effect in a transformation component (separated by commas), only the last effect in that component is applied.
>
>
> To combine effects, use separate components (separated by forward slashes) following best practice guidelines, which recommend including only one [action parameter](image_transformations#parameter_types) per component.

#### brightness

 `e_brightness:<level>`
Adjusts the image or video brightness.

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| level | integer | The level of brightness. The lower the number the lower the brightness.  **Range**: `-99 to 100`. **Default**: `80`. |

##### Example

Adjust an image brightness to 60 (`e_brightness:60`):

```
https://res.cloudinary.com/demo/image/upload/e_brightness:60/horses.jpg
```

#### saturation

 `e_saturation[:<level>]`
Adjusts an image or video saturation level.

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| level | integer | The level of saturation. The lower the number the lower the saturation.  **Range**: `-100 to 100`. **Default**: `80`. |

##### Example

Adjust image saturation to 70 (`e_saturation:70`):

```
https://res.cloudinary.com/demo/image/upload/e_saturation:70/horses.jpg
```

### f (format)


Converts (if necessary) and delivers an asset in the specified format regardless of the file [extension](#extension) used in the delivery URL.

Must be used for automatic format selection ([f_auto](#auto-3)) as well as when [fetching remote assets](fetch_remote_images#fetch_and_deliver_remote_files), while the file extension for the delivery URL remains the original file extension.

In most other cases, you can optionally use this transformation to change the format as an alternative to changing the file [extension](#extension) of the public ID in the URL to a supported format. Both will give the same result.

> Note
> In SDK **major versions** with initial release earlier than 2020, the name of this parameter is `fetch_format`. These SDKs also have a `format` parameter, which is not a transformation parameter, but is used to change the file extension, as shown in the [file extension examples - #2](#examples).
> The later SDKs have a single `format` parameter (which parallels the behavior of the `fetch_format` parameter of older SDKs). You can use this to change the actual delivered format of any asset, but if you prefer to convert the asset to a different format by changing the extension of the public ID in the generated URL, you can do that in these later SDKs by specifying the desired extension as part of the public ID value, as shown in [file extension examples - #1](#examples).

#### &lt;supported format&gt;

 `f_<supported format>`
Converts and delivers an asset in the specified format.

##### Optional qualifier

[e_camera](#camera)

**Learn more**: [Fetch format](image_format_support#fetch_format) | [Transcoding videos to other formats](video_transcoding)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| supported format | string | **Required.** The format to use when delivering the asset. **Possible values**: Any supported delivery format as relevant for the file type you are delivering:  - [Supported image formats](image_format_support#supported_image_formats) - [Supported video formats](video_transcoding#supported_video_formats) - [Supported audio formats](audio_transformations#supported_audio_formats) |

##### Examples

1. Convert and deliver a Photoshop image in JPG format (`f_jpg`):

  ```
  https://res.cloudinary.com/demo/image/upload/f_jpg/docs/cld_record_PSD.psd
  ```
2. Convert and deliver an MP4 video in WebM format (`f_webm`):

  ```
  https://res.cloudinary.com/demo/video/upload/f_webm/guy_woman_mobile.mp4
  ```

#### auto

 `f_auto[:media type]`
Automatically generates (if needed) and delivers an asset in the optimal format for the requesting browser in order to minimize the file size.

Optionally, include a media type to ensure the asset is delivered with the desired media type when no file extension is included. For example, when delivering a video using `f_auto` and no file extension is provided, the media type will default to an image unless `f_auto:video` is used.

> Note
> When used in conjunction with [automatic quality (q_auto)](image_optimization#automatic_quality_selection_q_auto), sometimes the selected format is not the one that minimizes file size, but rather the format that yields the optimal balance between smaller file size and good visual quality.

**Learn more**: [Image automatic format selection](image_optimization#automatic_format_selection_f_auto) | [Video automatic format selection](video_transcoding#f_auto)

##### Optional qualifiers

[fl_animated](#animated) | [fl_attachment](#attachment) | [fl_preserve_transparency](#preserve_transparency)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| media type | string | The media type to use when delivering the asset. **Possible values**: `image`, `video`, `animated`. |

##### Examples

1. Deliver the `play.jpg` image as a WebP, AVIF or JPEG XL, depending on the browser (or as a regular JPEG to browsers that support none of the aforementioned formats):

  ```
  https://res.cloudinary.com/demo/image/upload/f_auto/docs/play.jpg
  ```
2. Deliver the video as WebM (VP9) to Chrome browsers, MP4 (HEVC) to Safari browsers, or as an MP4 (H.264) to browsers that support neither of the aforementioned formats:

  ```
  https://res.cloudinary.com/demo/video/upload/f_auto/guy_woman_mobile.mp4
  ```
3. Deliver the video with automatic format selection, ensuring it is delivered as a video when no file extension is used:
  ```
  https://res.cloudinary.com/demo/video/upload/f_auto:video/guy_woman_mobile
  ```

### g (gravity)


A [qualifier](#parameter-types) that determines which part of an asset to focus on, and thus which part of the asset to keep, when any part of the asset is cropped. For overlays, this setting determines where to place the overlay.

**Learn more**: [Control image gravity](image_gravity) | [Control video gravity](video_resizing_and_cropping#control_gravity)

#### auto

 `g_auto[:<algorithm>][:<focal gravity>][:<thumb aggressiveness>][:thirds_0]`
A [qualifier](#parameter-types) to automatically identify the most interesting regions in the asset, and include in the crop.

> Notes
>
> - Automatic gravity is not supported for [animated images](animated_images). If `g_auto` is used in an animated image transformation, `center` gravity is applied, except when `c_fill_pad` is also specified, in which case an error is returned.
> - Any [custom coordinates](custom_focus_areas#custom_coordinates) defined for a specific image will override the automatic cropping algorithm and only the custom coordinates will be used 'as is' for the gravity, unless you specify 'custom_no_override' or 'none' as the **focal_gravity**.
> - If you're using our [Asia Pacific data center](admin_api#alternative_data_centers_and_endpoints_premium_feature), you currently can't apply `g_auto` to videos.

**Use with**: [c_auto - image only](#auto-1) | [c_auto_pad - image only](#auto_pad) | [c_crop - image only](#crop) | [c_fill](#fill) | [c_fill_pad](#fill_pad) | [c_lfill - image only](#lfill) | [c_thumb - image only](#thumb)

**Learn more**: [Automatic image cropping](image_automatic_gravity) | [Automatic video cropping](video_gravity)

**See also**: [fl_getinfo](#getinfo)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| algorithm | constant | **Image only**. The algorithm to apply: - `subject`: Applies deep-learning algorithms to identify the subjects of an image that are most likely to attract a person's gaze. - `classic`: Uses a combination of saliency heuristics to automatically detect significant regions in the image. |
| focal gravity | constant | Controls which elements are given higher priority for inclusion by the cropping algorithm.   **Images**  This value can be: - One of the focal gravity options as specified for [special positions](#special-position) (e.g.: `face`). - `aoi_<custom coordinates>` - an area of interest specified by custom coordinates of the form `<top left x>_<top left y>_<width>_<height>`. This overrides any custom coordinates already specified for an image (using the [Upload API](image_upload_api_reference) or the [Cloudinary Console](https://console.cloudinary.com/console)) (see [Custom coordinates on the fly](custom_focus_areas#custom_coordinates_on_the_fly)). - A specified object or category. You can specify one or more [supported objects or categories](cloudinary_ai_content_analysis_addon#supported_objects_and_categories), separated by colons (e.g.: `shoe:boot`). You can also specify the generic `g_auto:object` value to give priority to any detected object in the image. To use this option, you must be registered to the [Cloudinary AI Content Analysis](cloudinary_ai_content_analysis_addon) add-on.  Appending `_avoid` to the focal gravity minimizes the likelihood of including the specified [object](cloudinary_ai_content_analysis_object_aware_cropping#specifying_objects_to_avoid_using_auto_gravity)/[face](face_detection_based_transformations#position_overlays_avoiding_detected_faces)/[text](ocr_text_detection_and_extraction_addon#avoiding_text) in the crop. **Default:** `faces`.  ---  **Videos**  Possible values:   - `face`: Focuses the crop on the largest face detected in the video. - `faces`: Focuses the crop on all the detected faces in the video. - A specified object or category (see [Adjusting the automatic gravity focal preference for objects](video_gravity#auto_cropping_videos_to_focus_on_a_specified_object)).  **Default**: `null` (gaze prediction algorithm is used). |
| thumb aggressiveness | integer | **Image only**. Relevant only for 'thumb' cropping. The level of aggressiveness of the thumb cropping algorithm between 0 and 100. 100 keeps more of the original image. 0 crops more aggressively and zooms in. |
| thirds_0 | constant | **Image only**. Specify `thirds_0` to disable the [rule of thirds](image_automatic_gravity#the_rule_of_thirds) principle, resulting in the important elements being more centered, rather than offset according to the principle. |

##### Examples

1. Use the fill cropping mode to display a video in a square aspect ratio whilst keeping the dog as the main focus throughout (`ar_1:1,c_fill,g_auto,w_400`):

  ```
  https://res.cloudinary.com/demo/video/upload/ar_1:1,c_fill,g_auto,w_400/dog_orig_qflwce.mp4
  ```
2. Automatically crop an image to a square aspect ratio, based on the areas most likely to attract a person's initial gaze. (`ar_1:1,c_fill,g_auto:subject`):

  ```
  https://res.cloudinary.com/demo/image/upload/ar_1:1,c_fill,g_auto:subject/boat_lake2.jpg
  ```
3. Automatically crop an image to a square aspect ratio while focusing on a cat in the image (`ar_1:1,c_crop,g_auto:cat,w_1000`):

  ```
  https://res.cloudinary.com/demo/image/upload/ar_1:1,c_crop,g_auto:cat,w_1000/docs/one_cat_one_dog.jpg
  ```
4. Automatically crop an image using custom coordinates to specify the area of interest to keep (`g_auto:aoi_420_230_330_160`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_crop,g_auto:aoi_420_230_330_160,h_200,w_400/docs/addons/objectdetection/automobile-1853936_1920.jpg
  ```

### h (height)

 `h_<height value>`
A [qualifier](#parameter-types) that determines the height of a transformed asset or an overlay.

**Use with**: [c (crop/resize)](#c-cropresize) | [l (layer)](#l-layer) | [e_blur_region](#blur_region) | [e_pixelate_region](#pixelate_region) | [u (underlay)](#u-underlay)

**Learn more**: [Resizing and cropping images](resizing_and_cropping) | [Placing layers on images](layers) | [Placing layers on videos](video_layers)

**See also**: [w (width)](#w-width) | [ar (aspect ratio)](#ar-aspect-ratio) | [Arithmetic expressions](user_defined_variables#arithmetic_expressions)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| height value | integer \| float \| constant | **Required.** The height of the asset. Set to: - An **integer** value to set the height to the given number in pixels (e.g., `150` sets the height to exactly 150 pixels). - A **decimal** value to set the height to a multiple of the original dimension (e.g., `0.5` sets the height to half the original width). - `ih` to specify the initial height of the original image. |

##### Examples

1. Resize the image to a height of 150 pixels while maintaining aspect ratio (`c_scale,h_150`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_scale,h_150/face_top.jpg
  ```
2. Resize the image to 30% of its original size (`c_scale,h_0.3`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_scale,h_0.3/docs/flower_shop.jpg
  ```

### q (quality)

 `q_<quality value>`
Controls the quality of the delivered asset. Reducing the quality is a trade-off between visual quality and file size.

**Learn more**:

- [How to optimize image quality](image_optimization#how_to_optimize_image_quality)
- [How to optimize video quality](video_optimization#how_to_optimize_video_quality)

#### &lt;quality level&gt;

 `q_<quality level>[:qmax_<quant value>][:<chroma>]`
Sets the quality to the specified level.

> Caution
> A quality level of 100 can increase the file size significantly, particularly for video, as it is delivered lossless and uncompressed. As a result, a video with a quality level of 100 isn't playable on every browser.

**See also**: [Arithmetic expressions](user_defined_variables#arithmetic_expressions)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| quality level | integer | **Required.** The level of quality.  **Range**: `1 to 100`. |
| quant value | integer | **Videos only.** The maximum quantization value, used when transcoding to WebM (VP8/9). Helps to ensure that the video is not over-quantized, see [Control the quality of WebM transcoding](video_optimization#control_the_quality_of_webm_transcoding) for details. **Range**: `1 to 100`. **Default**: `100`. |
| chroma | constant | The chroma subsampling setting. See [Toggling chroma subsampling](image_optimization#toggle_chroma_subsampling) for details.**Possible values**:  - `420` - forces subsampling`444` - prevents subsampling. |

##### Examples

1. Deliver an image of the highest quality (302KB) (`q_100`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_100/docs/wines.jpg
  ```
2. Deliver a low quality image (44KB) (`q_20`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_20/docs/wines.jpg
  ```
3. Deliver a 60% quality image while forcing chroma subsampling (108KB) (`q_60:420`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_60:420/docs/wines.jpg
  ```
4. Transcode the first 30 seconds of a video to WebM with 70% quality, setting the maximum quantization to 20% (`q_70:qmax_20`):

  ```
  https://res.cloudinary.com/demo/video/upload/du_30.0/q_70:qmax_20/Liverpool_vs_Roma_full.webm
  ```

#### auto

 `q_auto[:<quality type>][:sensitive]`
Delivers an asset with an automatically determined level of quality.

**Learn more**: [Automatic quality for images](image_optimization#automatic_quality_selection_q_auto) | [Automatic quality for videos](video_optimization#automatic_quality_q_auto) | [Automatic quality for PDFs](pdf_optimization)

**Related flag**: [fl_any_format](#any_format)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| quality type | constant | The type of automatic quality. Not applicable to PDFs. **Possible values**:  - `best`: Ensures the best visual quality, using a less aggressive algorithm - `good`: Ensures optimal visual quality without affecting its perceptual quality - `eco`: Ensures a smaller file size using a more aggressive algorithm - `low`: Ensures the smallest file size using the most aggressive algorithm  **Default**: `good`. The addition of `:sensitive` (supported for images only) raises the quality level slightly, providing more granularity. For example, `q_auto:good:sensitive` gives a quality level above `good`, but not as good as the `best` level. (`q_auto:sensitive` is the same as `q_auto:good:sensitive`.) |

##### Examples

1. Automatically deliver a high quality image (174KB) (`q_auto:best`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_auto:best/docs/wines.jpg
  ```
2. Automatically deliver the optimal quality for an image: the smallest file size without affecting its visual quality (144KB) (`q_auto:good`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_auto:good/docs/wines.jpg
  ```
3. Automatically deliver a good quality image at a lower file size (113KB) (`q_auto:eco`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_auto:eco/docs/wines.jpg
  ```
4. Automatically deliver a small-sized image with low quality (95KB) (`q_auto:low`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_auto:low/docs/wines.jpg
  ```
5. Automatically deliver a small-sized image with quality between low and eco (102KB) (`q_auto:low:sensitive`):

  ```
  https://res.cloudinary.com/demo/image/upload/q_auto:low:sensitive/docs/wines.jpg
  ```


### w (width)


A [qualifier](#parameter-types) that sets the desired width of an asset using a specified value, or automatically based on the available width.

#### &lt;width value&gt;

 `w_<width value>`
A [qualifier](#parameter-types) that determines the width of a transformed asset or an overlay.

**Use with**: [c (crop/resize)](#c-cropresize) | [l (layer)](#l-layer) | [e_blur_region](#blur_region) | [e_pixelate_region](#pixelate_region) | [u (underlay)](#u-underlay)

**Learn more**: [Resizing and cropping images](resizing_and_cropping) | [Placing layers on images](layers) | [Placing layers on videos](video_layers)

**See also**: [h (height)](#h-height) | [ar (aspect ratio)](#ar-aspect-ratio) | [Arithmetic expressions](user_defined_variables#arithmetic_expressions)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| width value | integer \| float \| constant | **Required.** The width of the asset. Set to: - An **integer** value to set the width to the given number in pixels (e.g., `150` sets the width to exactly 150 pixels). - A **decimal** value to set the width to a multiple of the original dimension (e.g., `0.5` sets the width to half the original width). - `iw` to specify the initial width of the original image. |

##### Examples

1. Resize the image to a width of 100 pixels while maintaining aspect ratio (`c_scale,w_100`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_scale,w_100/face_top.jpg
  ```
2. Resize the image to 50% of its original width (`c_scale,w_0.5`):

  ```
  https://res.cloudinary.com/demo/image/upload/c_scale,w_0.5/docs/camera-640.jpg
  ```

#### auto

A [qualifier](#parameter-types) that determines how to automatically resize an image to match the width available for the image in a responsive layout. The parameter can be further customized by overriding the default [rounding step](#w_auto_rounding_step) or by using automatic [breakpoints](#w_auto_breakpoints).

<a id="w_auto_rounding_step"></a>

 `w_auto[:<rounding step>][:<fallback width>]`
The width is rounded up to the nearest rounding step (every 100 pixels by default) in order to avoid creating extra derived images and consuming too many extra transformations. Only works for certain browsers and when Client-Hints are enabled.

**Use with**: [c_limit](#limit)

**Learn more**: [Automatic image width](responsive_server_side_client_hints#automatic_image_width)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| rounding step | integer | Sets a new value for the rounding step (e.g.: `50`). **Default**: 100 |
| fallback width | integer | The width to use in the case the actual width cannot be retrieved from the Client-Hints header (e.g.: `500`). **Default**: Not set |

##### Examples

The HTML tag to deliver an image automatically scaled to the maximum width available (`sizes=100vw`) for the image (`c_limit,w_auto`):

You can create the HTML image tag above with our SDKs as follows:

<a id="w_auto_breakpoints"></a>

 `w_auto:breakpoints[_<breakpoint settings>][:<fallback width>][:json]`
The width is rounded up to the nearest breakpoint, where the optimal breakpoints are calculated using either the default breakpoint request settings or using the given settings.

**Use with**: [c_limit](#limit)

**Learn more**: [Responsive breakpoint request settings](image_upload_api_reference#responsive_breakpoints_parameter_request_settings)

##### Syntax details

| Value | Type | Description |
| --- | --- | --- |
| breakpoint settings | string | The breakpoint settings can be overridden by also including new breakpoint values. All 4 of the breakpoint request settings values must be included if you need to override any of them, and must be given in the following order: `_[min_width]_[max_width]_[bytes_step_in_KBs]_[max_images]` (e.g.: `w_auto:breakpoints_200_1920_30_15`). **Defaults**: min_width=50, max_width=1000, bytes_step=20KB, max_images=20. |
| fallback width | integer | The width to use in the case the actual width cannot be retrieved from the Client-Hints header (e.g.: `200`). **Default**: Not set |
| json | keyword | If `json` is specified, it requests that Cloudinary deliver the set of calculated breakpoints as a JSON response instead of delivering the transformed image itself. |

##### Examples

The HTML tag to deliver an image filled to an aspect ratio of 16:9 (`ar_16:9,c_fill`) and then automatically scaled to the closest optimal breakpoint, where the optimal breakpoints are calculated using breakpoint request values of min_width=200, max_width=1920, bytes_step=30, and max_images=15 (`c_limit,w_auto:breakpoints_200_1920_30_15`):

You can create the HTML image tag above with our SDKs as follows:

