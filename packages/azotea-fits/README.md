# azotea_fits

`azotea_fits` is a FITS image pre-processor for the **AZOTEA** program.

Its purpose is to adapt FITS headers produced by different image-capture applications to the metadata expected by AZOTEA. The program does not modify image data; it works on the headers of the primary HDU.

## Use cases

`azotea_fits` supports two use cases:

1. **Insert new keywords** that do not already exist in the original FITS file.
2. **Modify or normalize existing keywords** into the format expected by AZOTEA.

The second use case is only possible when the FITS header contains the `SWCREATE` keyword, which identifies the software that created the file. Therefore, if a file does not contain `SWCREATE`, the first step should be to assign it using the `creator` command.

The currently supported software creators are:

- `SharpCap`
- `CapturaFits`

For any other `SWCREATE` value, or when the keyword is missing, a generic editor is used. The generic editor can insert new keywords, but it cannot apply creator-specific corrections.

Adding support for a new FITS creator consists of implementing its metadata-fix and metadata-insert operations and registering them in the editor factory.

## Installation

```bash
pip install azotea-fits
```

The main CLI entry point is:

```bash
azofits --help
```

## Basic operation

All commands support two input modes:

- `-f`, `--image-file <path>`: process a single FITS file.
- `-d`, `--images-dir <path>`: recursively process all FITS files found below a directory.

The maximum search depth is controlled with:

```bash
--dir-depth <N>
```

The default value is `8`. A value of `0` means that only files directly inside the base directory are processed.

The recognized file extensions are:

```text
.fit
.fits
.fts
```

Extension matching is case-insensitive.

## Commands

### `creator`: set the FITS software creator

```bash
azofits -f image.fits creator --set sharpcap
```

Or, for a directory tree:

```bash
azofits -d ./night_20261026 creator --set capturafits
```

Allowed values are:

```text
sharpcap
capturafits
```

This command writes or updates the following FITS keyword:

```text
SWCREATE
```

It should be run before attempting to apply creator-specific corrections. Without `SWCREATE`, `azotea_fits` cannot select the appropriate adapter and can only perform generic metadata insertions.

### `view`: inspect metadata

```bash
azofits -f image.fits view
```

For a directory:

```bash
azofits -d ./night_20261026 view
```

This command displays a table with the FITS keywords relevant to AZOTEA, including:

| Field | FITS keyword |
|---|---|
| Camera | `INSTRUME` |
| Bayer pattern | `BAYERPAT` |
| Gain | `LOG_GAIN` |
| Bias | `PEDESTAL` |
| Pixel size X | `XPIXSIZE` |
| Pixel size Y | `YPIXSIZE` |
| Image type | `IMAGETYP` |
| Aperture diameter | `APTDIA` |
| Focal length | `FOCALLEN` |
| Observation date | `DATE-OBS` |
| Exposure time | `EXPTIME` |
| Software creator | `SWCREATE` |

### `edit`: insert or update metadata

```bash
azofits -f image.fits edit \
  --camera "ZWO ASI178MM" \
  --gain 120 \
  --bias 100 \
  --x-pixsize 2.8 \
  --y-pixsize 2.8 \
  --image-type light \
  --diameter 200 \
  --focal-length 1000 \
  --date-obs "2026-10-26T22:15:00" \
  --exptime 30 \
  --comment "Preprocessed with azofits"
```

To process a complete directory:

```bash
azofits -d ./night_20261026 edit \
  --camera "ZWO ASI178MM" \
  --gain 120 \
  --bias 100 \
  --x-pixsize 2.8 \
  --y-pixsize 2.8 \
  --image-type light \
  --diameter 200 \
  --focal-length 1000 \
  --date-obs "2026-10-26T22:15:00" \
  --exptime 30
```

Only the keywords associated with options explicitly provided on the command line are modified.

## `edit` options

| Option | FITS keyword | Unit / format |
|---|---|---|
| `--camera` | `INSTRUME` | Camera model |
| `--bayer-pattern` | `BAYERPAT` | Bayer pattern |
| `--gain` | `LOG_GAIN` | Gain in logarithmic scale |
| `--bias` | `PEDESTAL` | Global bias level |
| `--x-pixsize` | `XPIXSIZE` | Pixel width, µm |
| `--y-pixsize` | `YPIXSIZE` | Pixel height, µm |
| `--image-type` | `IMAGETYP` | Image type |
| `--diameter` | `APTDIA` | Optics diameter, mm |
| `--focal-length` | `FOCALLEN` | Focal length, mm |
| `--date-obs` | `DATE-OBS` | UTC date, `YYYY-MM-DDTHH:MM:SS` |
| `--exptime` | `EXPTIME` | Exposure time, s |
| `--comment` | `COMMENT` | Optional comment |

The values accepted by `--bayer-pattern` and `--image-type` come from the `BayerPattern` and `ImageType` enumerations defined by `lica_raw`.

The FITS keyword conventions referenced in external documentation remain valid. However, `azotea_fits` does not necessarily use those specific values for `IMAGETYP`; it uses the values defined by `ImageType` in `lica_raw`.

## Creator-specific corrections

In addition to the insertions requested on the command line, the `edit` command applies automatic corrections according to the software creator identified by `SWCREATE`.

### SharpCap

For files created by SharpCap, `azotea_fits` can:

- Read the camera model and gain from the auxiliary `*.CameraSettings.txt` file.
- Insert `INSTRUME` and `LOG_GAIN` when they are missing.
- Round `XPIXSIZE` and `YPIXSIZE` to two decimal places.
- Normalize Bayer-offset keywords.
- Correct the Bayer pattern when required.
- Remove microseconds from `DATE-OBS` when the value includes them.

### CapturaFits

For files created by CapturaFits, `azotea_fits` can:

- Derive the observation date from the file name.
- Derive the exposure time from the file name.
- Insert `DATE-OBS` and `EXPTIME` when they are missing.

## Change history

Every relevant modification is recorded in the FITS header using `HISTORY` entries.

To avoid generating a useless history, if the current value of a keyword already matches the value to be written, the header is not modified and no `HISTORY` entry is added.

Example generated entries:

```text
HISTORY INSTRUME: Old Camera => ZWO ASI178MM by azofits
HISTORY EXPTIME: 30.5 => 30.0 by azofits
HISTORY added DATE-OBS keyword
```

# Miscelanea

## Interesting links
[Interesting ClodyNights discussion](https://www.cloudynights.com/topic/692074-fits-keywords-bayerpat-bayoffx-bayoffy-etc/)

## FITS File Header Definitions

Copy of [Maxim DL FITS specifications](https://cdn.diffractionlimited.com/help/maximdl/FITS_File_Header_Definitions.htm)

Mandatory FITS keywords are as follows:

```
    SIMPLE – always ”T”, indicating a FITS header.

    BITPIX – indicates array format. Options include unsigned 8-bit (8), signed 16 bit (16), signed 32 bit (32), 32-bit IEEE float (-32), and 64-bit IEEE float (-64). The standard format is 16; -64 can be read by MaxIm DL but is not written.

    NAXIS – number of axes in the data array. MaxIm DL uses 2 for monochrome images, and 3 for color images.

    NAXIS1 – corresponds to the X axis.

    NAXIS2 – corresponds to the Y axis.

    NAXIS3 – present only for color images; value is always 3 (red, green, blue color planes are present in that order).
```

Optional keywords defined by the FITS standard and used in MaxIm DL:

```
    BSCALE – this value should be multiplied by the data array values when reading the FITS file. MaxIm DL always writes a value of 1 for this keyword.

    BZERO – this value should be added to the data array values when reading the FITS file. For 16-bit integer files, MaxIm DL writes 32768 (unless overridden by the Settings dialog).

    DATE-OBS – date of observation in the ISO standard 8601 format (Y2K compliant FITS): CCYY-MM-DDThh:mm:ss.sss. The Universal time at the start of the exposure is used. Note: the alternate format using DATE-OBS and TIME-OBS is not written, but MaxIm DL will correctly interpret it when read. The time is written to 10 ms resolution. The default behavior is to report the start of observation time, but individual camera drivers can change this.  As of Version 6.24 the DL Imaging driver sets the time to exposure midpoint.  

    HISTORY – indicates the processing history of the image. This keyword may be repeated as many times as necessary.

    INSTRUME – camera information. Either user entered or obtained from the camera driver.

    OBJECT – name or catalog number of object being imaged, if available from Observatory Control window or specified by the user in Settings.

    OBSERVER – user-entered information; the observer’s name.

    TELESCOP – user-entered information about the telescope used.
```

Extension keywords that may be added or read by MaxIm DL, depending on the current equipment and software configuration:

```
    AIRMASS – relative optical path length through atmosphere.

    AOCAMBT – ASCOM Observatory Conditions – Ambient temperature in degrees C

    AOCDEW – ASCOM Observatory Conditions – Dew point in degrees C

    AOCRAIN – ASCOM Observatory Conditions – Rain rate in mm/hour

    AOCHUM – ASCOM Observatory Conditions – Humidity in percent

    AOCWIND – ASCOM Observatory Conditions – Wind speed in m/s

    AOCWINDD – ASCOM Observatory Conditions – Wind direction in degrees (0..360)

    AOCWINDG – ASCOM Observatory Conditions – Wind gust in m/s

    AOCBAROM – ASCOM Observatory Conditions – Barometric pressure in hPa

    AOCCLOUD – ASCOM Observatory Conditions – Cloud coverage in percent

    AOCSKYBR – ASCOM Observatory Conditions – Sky brightness in Lux

    AOCSKYQU – ASCOM Observatory Conditions – Sky quality (magnitudes per square arcsecond)

    AOCSKYT – ASCOM Observatory Conditions – Sky temperature in degrees C

    AOCFWHM – ASCOM Observatory Conditions – Seeing FWHM in arc seconds

    APTDIA – diameter of the telescope in millimeters.

    APTAREA – aperture area of the telescope in square millimeters. This value includes the effect of the central obstruction.

    BAYERPAT – if present the image has a valid Bayer color pattern.

    BOLTAMBT – Boltwood Cloud Sensor ambient temperature in degrees C.

    BOLTCLOU – Boltwood Cloud Sensor cloud condition.

    BOLTDAY – Boltwood Cloud Sensor daylight level.

    BOLTDEW – Boltwood Cloud Sensor dewpoint in degrees C.

    BOLTHUM – Boltwood Cloud Sensor humidity in percent.

    BOLTRAIN – Boltwood Cloud Sensor rain condition.

    BOLTSKYT – Boltwood Cloud Sensor sky minus ambient temperature in degrees C.

    BOLTWIND – Boltwood Cloud Sensor wind speed in km/h.

    CALSTAT – indicates calibration state of the image; B indicates bias corrected, D indicates dark corrected, F indicates flat corrected.

    CENTAZ – nominal Azimuth of center of image in degrees.

    CENTALT – nominal Altitude of center of image in degress.

    CBLACK – indicates the black point used when displaying the image (screen stretch).

    CSTRETCH – initial display screen stretch mode.

    CCD-TEMP – actual measured sensor temperature at the start of exposure in degrees C. Absent if temperature is not available.

    COLORTYP – type of color sensor Bayer array or zero for monochrome.

    CWHITE – indicates the white point used when displaying the image (screen stretch).

    DATAMAX – pixel values above this level are considered saturated.

    DAVRAD – Davis Instruments Weather Station solar radiation in W/m^2

    DAVRAIN – Davis Instruments Weather Station accumulated rainfall in mm/day

    DAVAMBT – Davis Instruments Weather Station ambient temperature in deg C

    DAVDEW – Davis Instruments Weather Station dewpoint in deg C

    DAVHUM – Davis Instruments Weather Station humidity in percent

    DAVWIND – Davis Instruments Weather Station wind speed in km/h

    DAVWINDD – Davis Instruments Weather Station wind direction in deg

    DAVBAROM – Davis Instruments Weather Station barometric pressure in hPa

    EXPTIME – duration of exposure in seconds.

    DARKTIME – dark current integration time, if recorded. May be longer than exposure time.

    EGAIN – electronic gain in photoelectrons per ADU.

    FILTER – name of selected filter, if filter wheel is connected.

    FLIPSTAT – status of pier flip for German Equatorial mounts.

    FOCALLEN – focal length of the telescope in millimeters.

    FOCUSPOS – Focuser position in steps, if focuser is connected.

    FOCUSSSZ – Focuser step size in microns, if available.

    FOCUSTEM – Focuser temperature readout in degrees C, if available.

    IMAGETYP – type of image: Light Frame, Bias Frame, Dark Frame, Flat Frame, or Tricolor Image.

    INPUTFMT – format of file from which image was read.

    ISOSPEED – ISO camera setting, if camera uses ISO speeds.

    JD or JD_GEO – records the geocentric Julian Day of the start of exposure.

    JD-HELIO or JD_HELIO – records the Heliocentric Julian Date at the exposure midpoint.

    MIDPOINT – UT of midpoint of exposure.

    NOTES – user-entered information; free-form notes.

    OBJECT – name or designation of object being imaged.

    OBJCTALT – nominal altitude of center of image             

    OBJCTAZ – nominal azimuth of center of image

    OBJCTDEC – Declination of object being imaged, string format DD MM SS, if available. Note: this is an approximate field center value only.

    OBJCTHA – nominal hour angle of center of image

    OBJCTRA – Right Ascension of object being imaged, string format HH MM SS, if available. Note: this is an approximate field center value only.

    PEDESTAL – add this value to each pixel value to get a zero-based ADU. Calibration in MaxIm DL sets this to 100.

    PIERSIDE – indicates side-of-pier status when connected to a German Equatorial mount.

    READOUTM – records the selected Readout Mode (if any) for the camera.

    ROTATANG – Rotator angle in degrees, if focal plane rotator is connected.

    ROWORDER – Images taken by MaxIm DL are always TOP-DOWN.  

    SBSTDVER – string indicating the version of the SBIG FITS extensions supported.

    SET-TEMP – CCD temperature setpoint in degrees C. Absent if setpoint was not entered.

    SITELAT – latitude of the imaging site in degrees, if available. Uses the same format as OBJECTDEC.

    SITELONG – longitude of the imaging site in degrees, if available. Uses the same format as OBJECTDEC.

    SNAPSHOT – number of images combined.

    SWCREATE – string indicating the software used to create the file; will be ”MaxIm DL Version x.xx”, where x.xx is the current version number.

    SWMODIFY – string indicating the software that modified the file. May be multiple copies.

    TILEXY – indicates tile position within a mosaic.

    TRAKTIME – exposure time of the autoguider used during imaging.

    XBAYROFF – X offset of Bayer array on imaging sensor.

    YBAYROFF – Y offset of Bayer array on imaging sensor.

    XBINNING – binning factor used on X axis

    XORGSUBF – subframe origin on X axis

    XPIXSZ – physical X dimension of the sensor's pixels in microns (present only if the information is provided by the camera driver). Includes binning.

    YBINNING – binning factor used on Y axis

    YORGSUBF – subframe origin on Y axis

    YPIXSZ – physical Y dimension of the sensor's pixels in microns (present only if the information is provided by the camera driver). Includes binning.
```
