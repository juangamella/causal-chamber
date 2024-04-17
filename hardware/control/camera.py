import libsonyapi.camera
import requests
from requests.sessions import Session
import time
import sys

# TODO:
#  figure out how well flow with awaitTakePicture; if not, add manual delay?
#  implement burst shots
#  consider moving libsonyapi code here, or fork and keep as separate package


def to_float(param):
    """Transform a camera parameter (e.g. ISO, f-stop (aperture) or
    shutter speed) from string into a float.

    Examples
    --------
    >>> to_float("1/200")
    0.005
    >>> to_float('3"')
    180.0
    >>> to_float('1.8')
    1.8
    >>> to_float('22')
    22.0
    """
    if param[-1] == '"':
        return float(eval(param[:-1]) * 60)
    else:
        return float(eval(param))


class Camera(libsonyapi.camera.Camera):
    def __init__(self):
        super().__init__()
        self.update_info()
        print(self, file=sys.stderr)
        self.session = requests.Session()

    def take_single_shots(self, n, save=None, wait=2):
        for i in range(n):
            string = None if save is None else save % i
            self.take_single_shot(save=string)
            time.sleep(wait)

    def take_single_shot(self, save=None):
        # If necessary, switch the camera to the appropriate single-shot-mode
        if self.shooting_mode == "Continuous":
            self.set_shooting_mode("Single")
        # Wait for camera to be idle
        status = self.get_status()
        if status != "IDLE":
            print(f"  camera status is {status}... try again later", file=sys.stderr)
            return None
        # Take picture
        print(
            f"  taking picture - A : {self.aperture} - S : {self.shutter_speed} - I : {self.iso}",
            file=sys.stderr,
        )
        start = time.time()
        response = self._query_camera(Actions.actTakePicture, exceptions=False)
        print(response)
        if response.get("error", True):
            url = response["result"][0][0]
            print("  done (%0.2f seconds)" % (time.time() - start), file=sys.stderr)
            print(f"  url: {url}")
            if save is not None:
                self.download_image(url, save)
                print(f"  saved to: {save}")
        else:
            if response["error"][0] == 40403:
                self._query_camera(Actions.awaitTakePicture)
                self.take_single_shot(save)

    def get_status(self):
        response = self._query_camera(Actions.getEvent, False)
        return response["result"][1]["cameraStatus"]

    def set_shooting_mode(self, mode):
        if mode not in ["Single", "Continuous"]:
            raise ValueError("Unrecognized shooting mode")
        self._query_camera(Actions.setContShootingMode, {"contShootingMode": mode})

    def set_iso(self, param):
        if type(param) is not str:
            raise TypeError("Parameter must be a string")
        self._query_camera(Actions.setIsoSpeedRate, param)
        self.iso = param

    def set_aperture(self, param):
        if type(param) is not str:
            raise TypeError("Parameter must be a string")
        self._query_camera(Actions.setFNumber, param)
        self.aperture = param

    def set_shutter_speed(self, param):
        if type(param) is not str:
            raise TypeError("Parameter must be a string")
        self._query_camera(Actions.setShutterSpeed, param)
        self.shutter_speed = param

    def update_info(self):
        self.update_iso_info()
        self.update_aperture_info()
        self.update_shutter_speed_info()
        self.update_shooting_mode_info()

    def update_iso_info(self):
        response = self._query_camera(Actions.getAvailableIsoSpeedRate)
        self.available_isos = response["result"][1]
        self.iso = response["result"][0]

    def update_aperture_info(self):
        response = self._query_camera(Actions.getAvailableFNumber)
        self.available_apertures = response["result"][1]
        self.aperture = response["result"][0]

    def update_shutter_speed_info(self):
        response = self._query_camera(Actions.getAvailableShutterSpeed)
        self.available_shutter_speeds = response["result"][1]
        self.shutter_speed = response["result"][0]

    def update_shooting_mode_info(self):
        response = self._query_camera(Actions.getAvailableContShootingMode)
        self.shooting_mode = response["result"][0]["contShootingMode"]
        self.available_shooting_modes = response["result"][0]["candidate"]

    def _query_camera(self, action, params=[], exceptions=True):
        response = self.do(action, params)
        if exceptions and response.get("error", None) is not None:
            raise Exception(
                'CAMERA: action "%s"  returned an error: %s' % (action, response)
            )
        else:
            return response

    def __str__(self):
        info_string = ""

        info_string += "Model: %s\n" % self.name
        info_string += "API endpoint: %s\n" % self.camera_endpoint_url

        info_string += "\nShooting mode\n"
        info_string += "  current: %s\n" % self.shooting_mode
        info_string += "  available:\n  "
        for mode in self.available_shooting_modes:
            info_string += "  %s" % mode

        info_string += "\n\nAperture\n"
        info_string += "  current: %s\n" % self.aperture
        info_string += "  available:\n  "
        for aperture in self.available_apertures:
            info_string += "  %s" % aperture

        info_string += "\n\nISO\n"
        info_string += "  current: %s\n" % self.iso
        info_string += "  available:\n  "
        for iso in self.available_isos:
            info_string += "  %s" % iso

        info_string += "\n\nShutter Speed\n"
        info_string += " current: %s\n" % self.shutter_speed
        info_string += "  available:\n  "
        for shutter_speed in self.available_shutter_speeds:
            info_string += "  %s" % shutter_speed

        return info_string

    def download_image(self, url, destination):
        with self.session.get(url) as response:
            content = response.content
            with open(destination, "wb") as f:
                f.write(content)


class Actions(object):
    """
    contains string literals for all
    the function in sony camera api
    """

    setShootMode = "setShootMode"
    getShootMode = "getShootMode"
    getSupportedShootMode = "getSupportedShootMode"
    getAvailableShootMode = "getAvailableShootMode"
    actTakePicture = "actTakePicture"
    awaitTakePicture = "awaitTakePicture"
    startContShooting = "startContShooting"
    stopContShooting = "stopContShooting"
    startMovieRec = "startMovieRec"
    stopMovieRec = "stopMovieRec"
    startAudioRec = "startAudioRec"
    stopAudioRec = "stopAudioRec"
    startIntervalStillRec = "startIntervalStillRec"
    stopIntervalStillRec = "stopIntervalStillRec"
    startLoopRec = "startLoopRec"
    stopLoopRec = "stopLoopRec"
    startLiveview = "startLiveview"
    stopLiveview = "stopLiveview"
    startLiveviewWithSize = "startLiveviewWithSize"
    getLiveviewSize = "getLiveviewSize"
    getSupportedLiveviewSize = "getSupportedLiveviewSize"
    getAvailableLiveviewSize = "getAvailableLiveviewSize"
    setLiveviewFrameInfo = "setLiveviewFrameInfo"
    getLiveviewFrameInfo = "getLiveviewFrameInfo"
    actZoom = "actZoom"
    setZoomSetting = "setZoomSetting"
    getZoomSetting = "getZoomSetting"
    getSupportedZoomSetting = "getSupportedZoomSetting"
    getAvailableZoomSetting = "getAvailableZoomSetting"
    actHalfPressShutter = "actHalfPressShutter"
    cancelHalfPressShutter = "cancelHalfPressShutter"
    setTouchAFPosition = "setTouchAFPosition"
    getTouchAFPosition = "getTouchAFPosition"
    cancelTouchAFPosition = "cancelTouchAFPosition"
    actTrackingFocus = "actTrackingFocus"
    cancelTrackingFocus = "cancelTrackingFocus"
    setTrackingFocus = "setTrackingFocus"
    getTrackingFocus = "getTrackingFocus"
    getSupportedTrackingFocus = "getSupportedTrackingFocus"
    getAvailableTrackingFocus = "getAvailableTrackingFocus"
    setContShootingMode = "setContShootingMode"
    getContShootingMode = "getContShootingMode"
    getSupportedContShootingMode = "getSupportedContShootingMode"
    getAvailableContShootingMode = "getAvailableContShootingMode"
    setContShootingSpeed = "setContShootingSpeed"
    getContShootingSpeed = "getContShootingSpeed"
    getSupportedContShootingSpeed = "getSupportedContShootingSpeed"
    getAvailableContShootingSpeed = "getAvailableContShootingSpeed"
    setSelfTimer = "setSelfTimer"
    getSelfTimer = "getSelfTimer"
    getSupportedSelfTimer = "getSupportedSelfTimer"
    getAvailableSelfTimer = "getAvailableSelfTimer"
    setExposureMode = "setExposureMode"
    getExposureMode = "getExposureMode"
    getSupportedExposureMode = "getSupportedExposureMode"
    getAvailableExposureMode = "getAvailableExposureMode"
    setFocusMode = "setFocusMode"
    getFocusMode = "getFocusMode"
    getSupportedFocusMode = "getSupportedFocusMode"
    getAvailableFocusMode = "getAvailableFocusMode"
    setExposureCompensation = "setExposureCompensation"
    getExposureCompensation = "getExposureCompensation"
    getSupportedExposureCompensation = "getSupportedExposureCompensation"
    getAvailableExposureCompensation = "getAvailableExposureCompensation"
    setFNumber = "setFNumber"
    getFNumber = "getFNumber"
    getSupportedFNumber = "getSupportedFNumber"
    getAvailableFNumber = "getAvailableFNumber"
    setShutterSpeed = "setShutterSpeed"
    getShutterSpeed = "getShutterSpeed"
    getSupportedShutterSpeed = "getSupportedShutterSpeed"
    getAvailableShutterSpeed = "getAvailableShutterSpeed"
    setIsoSpeedRate = "setIsoSpeedRate"
    getIsoSpeedRate = "getIsoSpeedRate"
    getSupportedIsoSpeedRate = "getSupportedIsoSpeedRate"
    getAvailableIsoSpeedRate = "getAvailableIsoSpeedRate"
    setWhiteBalance = "setWhiteBalance"
    getWhiteBalance = "getWhiteBalance"
    getSupportedWhiteBalance = "getSupportedWhiteBalance"
    getAvailableWhiteBalance = "getAvailableWhiteBalance"
    actWhiteBalanceOnePushCustom = "actWhiteBalanceOnePushCustom"
    setProgramShift = "setProgramShift"
    getSupportedProgramShift = "getSupportedProgramShift"
    setFlashMode = "setFlashMode"
    getFlashMode = "getFlashMode"
    getSupportedFlashMode = "getSupportedFlashMode"
    getAvailableFlashMode = "getAvailableFlashMode"
    setStillSize = "setStillSize"
    getStillSize = "getStillSize"
    getSupportedStillSize = "getSupportedStillSize"
    getAvailableStillSize = "getAvailableStillSize"
    setStillQuality = "setStillQuality"
    getStillQuality = "getStillQuality"
    getSupportedStillQuality = "getSupportedStillQuality"
    getAvailableStillQuality = "getAvailableStillQuality"
    setPostviewImageSize = "setPostviewImageSize"
    getPostviewImageSize = "getPostviewImageSize"
    getSupportedPostviewImageSize = "getSupportedPostviewImageSize"
    getAvailablePostviewImageSize = "getAvailablePostviewImageSize"
    setMovieFileFormat = "setMovieFileFormat"
    getMovieFileFormat = "getMovieFileFormat"
    getSupportedMovieFileFormat = "getSupportedMovieFileFormat"
    getAvailableMovieFileFormat = "getAvailableMovieFileFormat"
    setMovieQuality = "setMovieQuality"
    getMovieQuality = "getMovieQuality"
    getSupportedMovieQuality = "getSupportedMovieQuality"
    getAvailableMovieQuality = "getAvailableMovieQuality"
    setSteadyMode = "setSteadyMode"
    getSteadyMode = "getSteadyMode"
    getSupportedSteadyMode = "getSupportedSteadyMode"
    getAvailableSteadyMode = "getAvailableSteadyMode"
    setViewAngle = "setViewAngle"
    getViewAngle = "getViewAngle"
    getSupportedViewAngle = "getSupportedViewAngle"
    getAvailableViewAngle = "getAvailableViewAngle"
    setSceneSelection = "setSceneSelection"
    getSceneSelection = "getSceneSelection"
    getSupportedSceneSelection = "getSupportedSceneSelection"
    getAvailableSceneSelection = "getAvailableSceneSelection"
    setColorSetting = "setColorSetting"
    getColorSetting = "getColorSetting"
    getSupportedColorSetting = "getSupportedColorSetting"
    getAvailableColorSetting = "getAvailableColorSetting"
    setIntervalTime = "setIntervalTime"
    getIntervalTime = "getIntervalTime"
    getSupportedIntervalTime = "getSupportedIntervalTime"
    getAvailableIntervalTime = "getAvailableIntervalTime"
    setLoopRecTime = "setLoopRecTime"
    getLoopRecTime = "getLoopRecTime"
    getSupportedLoopRecTime = "getSupportedLoopRecTime"
    getAvailableLoopRecTime = "getAvailableLoopRecTime"
    setWindNoiseReduction = "setWindNoiseReduction"
    getWindNoiseReduction = "getWindNoiseReduction"
    getSupportedWindNoiseReduction = "getSupportedWindNoiseReduction"
    getAvailableWindNoiseReduction = "getAvailableWindNoiseReduction"
    setAudioRecording = "setAudioRecording"
    getAudioRecording = "getAudioRecording"
    getSupportedAudioRecording = "getSupportedAudioRecording"
    getAvailableAudioRecording = "getAvailableAudioRecording"
    setFlipSetting = "setFlipSetting"
    getFlipSetting = "getFlipSetting"
    getSupportedFlipSetting = "getSupportedFlipSetting"
    getAvailableFlipSetting = "getAvailableFlipSetting"
    setTvColorSystem = "setTvColorSystem"
    getTvColorSystem = "getTvColorSystem"
    getSupportedTvColorSystem = "getSupportedTvColorSystem"
    getAvailableTvColorSystem = "getAvailableTvColorSystem"
    startRecMode = "startRecMode"
    stopRecMo = "stopRecMo"
    getEvent = "getEvent"


# ----------------------------------------------------------------------
# Doctests
if __name__ == "__main__":
    import doctest

    doctest.testmod(
        extraglobs={},
        verbose=True,
        optionflags=doctest.ELLIPSIS,
    )
