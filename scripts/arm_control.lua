function sysCall_init()
    -- Initialize handles
    robotBase = sim.getObject('.')  -- Get the robot base
    jointHandles = {}
    for i=1,6 do
        jointHandles[i] = sim.getObject('./Joint'..i)
    end
    
    -- Get target dummy handle
    targetHandle = sim.getObject('./Target')
    
    -- Initialize IK environment
    ikEnv = sim.createEnvironment()
    
    -- Create IK group
    ikGroup = sim.createIkGroup(ikEnv)
    
    -- Create IK elements
    tip = sim.getObject('./Joint6')
    target = targetHandle
    
    -- Add IK elements
    sim.createIkElement(ikGroup, sim.ik_1x_sphere, {tip}, {target}, {1, 1, 1}, {0.1, 0.1, 0.1}, {0.1, 0.1, 0.1})
    
    -- Enable the remote API
    sim.setInt32Parameter(sim.intparam_server_port_start, 19999)
    sim.startSimulation()
end

function sysCall_actuation()
    -- This function is called every simulation step
    -- Calculate IK
    if sim.handleIkGroup(ikGroup) == sim.ikresult_success then
        -- IK was solved successfully
        -- You can add additional control logic here
    end
end

function sysCall_cleanup()
    -- Clean up
    if ikEnv then
        sim.destroyEnvironment(ikEnv)
    end
    sim.stopSimulation()
end

-- Function to handle inverse kinematics
function solveIK()
    local targetPos = sim.getObjectPosition(targetHandle, -1)
    local targetOri = sim.getObjectOrientation(targetHandle, -1)
    
    -- Calculate IK
    local result = sim.handleIkGroup(ikGroup)
    
    if result == sim.ikresult_success then
        -- Get and apply joint angles
        for i=1,#jointHandles do
            local currentPos = sim.getJointPosition(jointHandles[i])
            sim.setJointTargetPosition(jointHandles[i], currentPos)
        end
        return true
    end
    return false
end

-- Function to check joint limits
function checkJointLimits(jointAngles)
    for i=1,#jointHandles do
        local cyclic, interval = sim.getJointInterval(jointHandles[i])
        if not cyclic then
            if jointAngles[i] < interval[1] or jointAngles[i] > interval[2] then
                return false
            end
        end
    end
    return true
end

-- Function to get current joint positions
function getJointPositions()
    local positions = {}
    for i=1,#jointHandles do
        positions[i] = sim.getJointPosition(jointHandles[i])
    end
    return positions
end

-- Function to set joint positions
function setJointPositions(positions)
    if #positions == #jointHandles and checkJointLimits(positions) then
        for i=1,#jointHandles do
            sim.setJointTargetPosition(jointHandles[i], positions[i])
        end
        return true
    end
    return false
end 