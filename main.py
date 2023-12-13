import linear_problem as lp

print("==============================Network Program Start==============================")

def makeLists(problem, streetFile, cameraFile, outputFile):
    problem.setStreetFile(streetFile)
    problem.setCameraFile(cameraFile)
    problem.listAllStreets()
    outputFile.write("Streets: " + str(problem.all_streets) + " \n")
    problem.listAllIntersections()
    outputFile.write("Intersections: " + str(problem.all_intersections) + " \n")
    problem.listCameras()
    outputFile.write("Intersections with cameras: " + str(problem.cameras_list) + " \n")
    problem.listNoCameraStreets(False)
    problem.listOnlyCameraStreets(True)
    problem.listNoCameraIntersections()
    
def solver(problem, file):
    budget = int(input("enter a redlight budget: "))
    file.write("Red Light Budget: " + str(budget) + "\n")
    source = int(input("enter a source node: "))
    file.write("Source node: " + str(source) + "\n")
    destination = int(input("enter a destination node: "))
    file.write("Destination node: " + str(destination) + "\n")

    output = problem.find_shortest_path(source, destination, budget)

    if output[2]:
        print("Best budgeted path:")
        print(output[0])
        file.write("Best path:\n")
        file.write(str(output[0]) + "\n")
        print("Best travel time: ")
        print(output[1])
        file.write("Best travel time: \n")
        file.write(str(output[1]) + "\n")
    else:
        print("Budgeted route not possible!")
        file.write("No solution found. \n")
    return (output[0], output[1], output[2])

def main():
    # Create a linear problem object, this will store lists and file names
    linear_problem = lp.LinearProblem()
    # Initialize some variables that will be used later
    first_loop = True
    street_file = None
    camera_file = None
    sessionNumber = 0

    # Create a file called transcript.txt, will overwrite any current text
    f = open("transcript.txt", "w")

    # Main loop
    while(True):
        input("Press enter to start new session.")
        sessionNumber+=1
        f.write("======================================Session {}======================================\n".format(sessionNumber))

        # First time running will run this
        if first_loop:
            first_loop = False
            street_file = input("Enter the file name for the street list: ")
            camera_file = input("Enter the file name for the camera list: ")        
        else:
            if input("using new street file? last street file was {} (y/n) ".format(street_file)) == "y":
                street_file = input("Enter the file name for the street list: ")
            if input("using new camera file? last camera file was {} (y/n) ".format(camera_file)) == "y":
                camera_file = input("Enter the file name for the camera list: ")
        
        f.write("Street file used: {}\n".format(street_file))
        f.write("Camera file used: {}\n".format(camera_file))
        makeLists(linear_problem, street_file, camera_file, f)
        
        solver(linear_problem, f)

        if input("start new session? (y/n) ") != "y":
            print("ending session...")
            break
    
    print("exiting...")
    f.write("====================================End of Program====================================")
    f.close()
    exit()

# Call the main() function
main()









# source = input("Start Node: ")
# destination = input("End Node: ")

# budget = input("Please enter a number for the budget: ")
# if not budget.isnumeric() or not source.isnumeric() or not destination.isnumeric():
#     print("Invalid input. Exiting...")
#     exit()

# budget = int(budget)
# source = int(source)
# destination = int(destination)

# budget = 1
# source = 261114812
# destination = 733296075

# streets = problem.all_streets
# intersections = problem.all_intersections
# budgetedOutput = problem.budgeted_shortest_path(source, destination, streets, intersections, budget)
# print("============================================================")
# if budgetedOutput[2]:
#     print("Best budgeted path:")
#     print(budgetedOutput[0])
#     print("Best travel time: ")
#     print(budgetedOutput[1])
# else:
#     print("Budgeted route not possible, exiting...")
#     exit()
