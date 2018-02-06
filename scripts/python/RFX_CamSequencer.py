import os.path
import json
import hou.session
from os.path import basename

def ShowError(text):
    hou.ui.displayMessage(text,severity=hou.severityType.Error)
    
def FindNodeByName(name, parent):
    for childnode in parent.children():
        if childnode.name() == name:
            return childnode
    return None
    
def FindInArray(name, array):
    for element in array:
        if element.name() == name:
            return element
    return None
    
def DeleteUnusedCams(array):
    for camera in array:
        camera.destroy()
        
def CheckHouFps():
    if hou.fps() != 30:
        result = hou.ui.displayMessage("FPS are not set to 30, please do something.",buttons=('Set to 30 and continue.','Cancel operation.',), severity=hou.severityType.Error)
        if result == 0:
            hou.setFps(30)
            return True
        elif result == 1:
            return False
    return True

def RunTool():
    if CheckHouFps() == False:
        return

    fbx_filename = hou.ui.selectFile(file_type=hou.fileType.Any, pattern="*.fbx")#"C:\DNE\PG5\Anim\Cameras\MS_E1_7A_PowerReveal.fbx" #
    print ("fbx : %s" % fbx_filename)
    json_filename = fbx_filename.replace(".fbx", ".json")
    print ("json : %s" % json_filename)
    
    if (not os.path.isfile(fbx_filename)):
        ShowError("Can't find file %s"%fbx_filename)
        return
    if (not os.path.isfile(json_filename)):
        ShowError("Can't find file %s"%json_filename)
        return
        
    filename = "%s_Cameras" % os.path.splitext(basename(fbx_filename))[0]
    
    #Check if a node with the same name already exists
    existing_node = hou.node("/obj/%s" % filename)
    if (existing_node != None):
        existing_node.destroy()
    
    fbx_node, other = hou.hipFile.importFBX(fbx_filename,convert_into_y_up_coordinate_system=True)
    fbx_node.setName(filename)
    fbx_node_scale = fbx_node.parm("scale")
    fbx_node_scale.set(0.01)
    
    cameras = []
    
    for childnode in fbx_node.children():
        if childnode.type().name() == "cam":
            cam_scale = childnode.parm("iconscale")
            cam_scale.set(400)
            cameras.append(childnode)
            
    #create switcher
    #switcher_node = FindNodeByName("cam_switcher", fbx_node)
    #if(switcher_node == None):
    switcher_node = fbx_node.createNode("switcher", "cam_switcher")
    
    #chop node to manage camaera offset
    chop_node = fbx_node.createNode("chopnet", "chop_chop")
    
    #create sub nodes of the chop network
    fetchedChans= "t[xyz] r[xyz] focal"
    
    playback_start = 1
    playback_end = 1
        
    #parse the json
    with open(json_filename) as data_file:    
        json_data = json.load(data_file)
        camera_data = json_data["cameras"]

        shot_count = 0
        for shot in camera_data:
            current_shot = camera_data[shot]
            
            #update min/max playback range
            if current_shot["start"] < playback_start:
                playback_start = current_shot["start"]
                
            if current_shot["end"] > playback_end:
                playback_end = current_shot["end"]
            
            associated_camera_name = current_shot["name"]
            
            current_cam = FindInArray(associated_camera_name, cameras)
            associated_cam = hou.copyNodesTo([current_cam] , fbx_node)[0]
 
            switcher_node.setInput(shot_count,associated_cam)
            
            switcher_keyed_parm = switcher_node.parm("camswitch")
            keyframe = hou.Keyframe()
            keyframe.setTime(current_shot["start"] ) #current_shot["start"] + current_shot["startshot"]
            #print("Switcher_Key %s"%(current_shot["start"] * hou.fps()))
            keyframe.setValue(shot_count)
            keyframe.setExpression("constant()", hou.exprLanguage.Hscript)
            switcher_keyed_parm.setKeyframe(keyframe)
            
            #handle offset with fetch nodes
            camTimeOffset = (current_shot["offset"] - current_shot["start"]) * hou.fps()*-1
            #print camTimeOffset
            
            fetchNode = chop_node.createNode('fetch')
            fetchCamPath = associated_cam.path()
            #print fetchCamPath
            fetchNode.parm('path').set(fetchedChans)
            fetchNode.parm('nodepath').set(fetchCamPath)
            fetchNode.parm('rate').set(hou.fps())
            
            resampleNode= fetchNode.createOutputNode("resample", "rs_%s"%shot_count)
            
            resampleNode.parm('method').set(3)
            resampleNode.parm('units').set(0)
            resampleNode.parm('rate').set(hou.fps())#hou.fps() * (1 +(1-current_shot["timescale_camera"]))
            
            resampleNode.parm('start').set(camTimeOffset)
            resampleNode.parm('end').set(camTimeOffset)
            resampleNode.parm('scope').set(fetchedChans)
            resampleNode.parm('export').set(fetchCamPath)
            
            resampleNode.setDisplayFlag(1)
    
            resampleNode.setExportFlag(1) 
    
            fetchNode.cook(force=True)
            
            shot_count += 1
    
    #set the playback range
    hou.playbar.setPlaybackRange(playback_start * hou.fps(), playback_end* hou.fps())
    
    DeleteUnusedCams(cameras)
    print "Camera Setup Done"
        
RunTool()

