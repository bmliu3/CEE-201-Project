from pulp import *
import numpy as np
from itertools import combinations

class LinearProblem:
    def __init__(self):
        self.streetFile = None
        self.cameraFile = None
        self.sameStreetFile = False
        self.sameCameraFile = False
        self.all_intersections = []
        self.all_streets = []
        self.cameras_list = []
        self.only_camera_streets = []
        self.no_camera_streets = []
        self.no_camera_intersections = []
             
    def setStreetFile(self, input):
        if self.streetFile == input:
            self.sameStreetFile = True
            return
        self.streetFile = input
    
    def setCameraFile(self, input):
        if self.cameraFile == input:
            self.sameCameraFile = True
            return
        self.cameraFile = input
        
    def convertVariableToTuple(self, input):
        value = input.split("_")
        newValue = eval(value[1] + " " + value[2])
        return newValue
    
    def listAllStreets(self):
        if self.sameStreetFile:
            return
        with open("{}".format(self.streetFile)) as file:
            data = [line.rstrip() for line in file]
        
        self.all_streets = []
        print("making new street list...")
        for line in data:
            l = line.split()
            self.all_streets.append((int(l[0]), int(l[1]), float(l[2])))
            self.all_streets.append((int(l[1]), int(l[0]), float(l[2])))
        print("done.")
        return

    def listAllIntersections(self):
        if self.sameStreetFile:
            return
        with open("{}".format(self.streetFile)) as file:
            data = [line.rstrip() for line in file]

        self.all_intersections = []
        print("making new intersections list...")
        for line in data:
            l = line.split()
            self.all_intersections.append(int(l[0]))
            self.all_intersections.append(int(l[1]))
        self.all_intersections = list(np.unique(self.all_intersections))
        print("done.")
        return 

    def listCameras(self):
        if self.sameCameraFile:
            return
        with open("{}".format(self.cameraFile)) as file:
            data = [line.rstrip() for line in file]

        self.cameras_list = []
        print("making new camera list...")
        for line in data:
            self.cameras_list.append(int(line))
        print("done.")
        return 

    def listNoCameraStreets(self, ranOther):
        if self.sameCameraFile and self.sameStreetFile:
            return
        print("making new list of streets with no cameras...")
        if ranOther:
            self.no_camera_streets = list(set(self.all_streets) - set(self.only_camera_streets))
            print("done.")
            print(self.no_camera_streets)
            return
        no_cameras = []
        for street in self.all_streets:
            if street[0] not in self.cameras_list and street[1] not in self.cameras_list:
                no_cameras.append(street)
        self.no_camera_streets = no_cameras
        print("done.")
        print(self.no_camera_streets)
        return 

    def listNoCameraIntersections(self):
        if self.sameCameraFile and self.sameStreetFile:
            return
        print("making new list of intersections without cameras...")
        self.no_camera_intersections = list(set(self.all_intersections) - set(self.cameras_list))
        print("done.")
        print(self.no_camera_intersections)
        return 

    def listOnlyCameraStreets(self, ranOther):
        if self.sameCameraFile and self.sameStreetFile:
            return
        print("making new list of only streets with cameras...")
        if ranOther:
            self.only_camera_streets = list(set(self.all_streets) - set(self.no_camera_streets))
            print("done.")
            print(self.only_camera_streets)
            return
        only_cameras = []
        for street in self.all_streets:
            if street[0] in self.cameras_list or street[1] in self.cameras_list:
                only_cameras.append(street)
        self.only_camera_streets = only_cameras
        print("done.")
        print(self.only_camera_streets)
        return 

    def calculate_model(self, source, terminal, streets, intersections):
        # See practice problem for documentation on how this works
        print("---------------------------calculate_model---------------------------")

        model = LpProblem("Shortest_Path_Problem", LpMinimize)
        print("making decision variable index...")
        xindx = []
        for street in streets:
            xindx.append((street[0], street[1]))
        print("done.")

        x = LpVariable.dicts("X", xindx,0,None) #setting up x variables and nonnegativity constraints
        print("assigning values to decision variables...")
        model += lpSum([street[2]*x[street[0], street[1]] for street in streets])
        for i in intersections:
            if i==source:
                model+=lpSum([x[street[0],street[1]]-x[street[1],street[0]] for street in streets if street[0]==i])==1, "source"
            elif i==terminal:
                model+=lpSum([x[street[0],street[1]]-x[street[1],street[0]] for street in streets if street[0]==i])==-1, "destination"
            else:
                model+=lpSum([x[street[0],street[1]]-x[street[1],street[0]] for street in streets if street[0]==i])==0, "node "+str(i)
        print("done.")        
        print("now solving...")
        model.solve()
        print("solving step done.")
        print('Status:',LpStatus[model.status])
        for v in model.variables():
            if v.varValue==1:
                print(v.name, '=', v.varValue)
        print('The travel time is', value(model.objective))
        print("---------------------------------------------------------------------------")

        # Return a model containing the optimized path
        return model
    
    def calculate_path(self, model):
        path = []
        for v in model.variables():
            if v.varValue==1:
                v_tuple = self.convertVariableToTuple(v.toDict()['name'])
                path.append(v_tuple)
        # return an array of street tuples that represents the path
        return path

    def calculate_path_time(self, model):
        return value(model.objective)

    def listPathRedlights(self, path):
        redlights = []
        for street in path:
            if street[0] in self.cameras_list:
                redlights.append(street[0])
            if street[1] in self.cameras_list:
                redlights.append(street[1])
                
        redlights = list(np.unique(redlights))
        return redlights
    
    def find_shortest_path(self, source, terminal, budget):
        print("---------------------------Finding Shortest Path---------------------------")

        # Define what the unrestricted path is and find out what redlights lie on the path
        print("calculating unrestricted model...")
        unrestricted_model = self.calculate_model(source, terminal, self.all_streets, self.all_intersections)
        print("unrestricted model done.")
        unrestricted_path = self.calculate_path(unrestricted_model)
        print("unrestricted path: {}".format(unrestricted_path) )
        print("length of unrestricted path: ", len(unrestricted_path))
        unrestricted_time = self.calculate_path_time(unrestricted_model)
        redlights = self.listPathRedlights(unrestricted_path)
        print("list of redlights: ", redlights)

        # First check if we even need to calculate with budget
        if budget == 0:
            print("budget is 0")
            if int(source) in self.cameras_list:
                print("source node is a redlight intersection with a camera.")
            if int(terminal) in self.cameras_list:
                print("terminal node is a redlight intersection with a camera.")
            else:
                # This means we want to avoid all red lights
                # Return completely restricted path
                print("calculating restricted model...")
                
                restricted_model = self.calculate_model(int(source), int(terminal), self.no_camera_streets, self.no_camera_intersections)
                print("calculating restricted model done.")
                restricted_path = self.calculate_path(restricted_model)
                restricted_time = self.calculate_path_time(restricted_model)
                if restricted_model.status != -1:
                    return (restricted_path, restricted_time, True)
            return(0,0,False)
            
        elif int(len(redlights)) <= int(budget):
            print("on budget")
            # We are within the budget, so return shortest path (do nothing)
            if unrestricted_model.status != -1:
                return (unrestricted_path, unrestricted_time, True)
            else:
                return (0, 0, False)
        
        # Make a list of all combination of red light intersections along the path
        feasible_redlights = list(combinations(redlights, budget))

        # Initialize some variables
        shortest_time = -1
        best_path = []
        budgetedPathPossible = False
        # For each combination in the feasibile red light list
        print("calculating best budgeted path...")
        for combo in feasible_redlights:
            # Make a temporary list of intersections that is made up of intersections with no cameras
            # and the specific combination of intersections
            newIntersections = np.array(combo)
            temp_intersections = np.array(self.listNoCameraIntersections())
            temp_intersections = list(np.concatenate((temp_intersections, newIntersections)))

            # Add streets with those intersections and streets with no cameras to a list
            # no camera streets + specific redlight streets = new list of streets
            temp_streets = self.no_camera_streets
            for street in self.only_camera_streets:
                for intersection in combo:
                    if int(intersection) == int(street[0]) or int(intersection) == int(street[1]):
                        temp_streets.append(street)

            # Calculate the path and path time of the combination of intersections
            
            combinationModel = self.calculate_model(source, terminal, temp_streets, temp_intersections)
            if combinationModel.status != -1:
                budgetedPathPossible = True
            path = self.calculate_path(combinationModel)
            path_time = self.calculate_path_time(combinationModel)

            # Check if it is the first combination
            if shortest_time < 0:
                # If it is, make the first combination the starting comparison
                shortest_time = path_time
                best_path = path
            elif shortest_time > path_time:
                # Otherwise, check if the time of the current combination beats previous best times
                shortest_time = path_time
                best_path = path
        print("done.")
        return (best_path, shortest_time, budgetedPathPossible)
            

        



