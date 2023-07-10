import Metashape
import os, sys
import time, datetime
import math
import json

if len(sys.argv) > 1:
    # Define Image Path from user input
    # Path should be to the raw image folder
    proQ = sys.argv[1]

else:
    # Quit if no path given
    print("Please put the path to your Processing Queue in as an argument")
    sys.exit(1)

proQ = open(sys.argv[1], "r")
lines = proQ.readlines()
ProcessingQueue = []
for line in lines:
    if line[-1] == '\n':
        ProcessingQueue.append(line[:-1])
    else:
        ProcessingQueue.append(line)

print(ProcessingQueue)
print("Number of sites to be processed:" + str(len(ProcessingQueue)))

for pq in ProcessingQueue:
    # Define Image Path from user input
    img_path = pq
    proj_dir, jpeg_name = os.path.split(img_path)
    base_dir, img_folder = os.path.split(proj_dir)
    print("proj_dir: " + str(proj_dir))
    print("base_dir: " + str(base_dir))
    print("jpeg_name: " + str(jpeg_name))

    proj_name = str(jpeg_name.rsplit('_', 1)[0])
    print("proj_name: " + str(proj_name))

    export_folder = proj_name
    agisoft_files = "Agisoft_Project_Data_Exports"
    export_path = os.path.join(base_dir, agisoft_files, export_folder)
    print("export_path: " + str(export_path))

    # Define Start Time
    start_time = time.time()
    print_time = time.ctime(start_time)
    print("Start Time: ", print_time)

    # Define which document
    doc = Metashape.app.document
    doc.open(export_path + '/' + proj_name + '.psx')
    # doc.save(export_path + '/' + proj_name + '.psx')
    # doc.save()

    # Define which Chunk
    # chunk = add.Chunk()
    chunk = Metashape.app.document.chunk

    has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

    if has_transform:
        if not chunk.elevation:
            print("Building DEM")
            chunk.buildDem(source_data=Metashape.DenseCloudData)
            doc.save()
            print("Finished DEM")

        if not chunk.orthomosaic:
            print("Building Orthophotomosaic")
            chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
            doc.save()
            print("Finished building orthophotomosaic")

        # if not chunk.tiled_model:
        #    chunk.buildTiledModel(source_data=Metashape.DenseCloudData)
        #    doc.save()

    ## Export Results
    print("Exporting Products")

    # Export Report
    print("Exporting Report")
    today = datetime.datetime.now()
    # Textual month, day and year
    d3 = today.strftime("%B %d, %Y")

    chunk.exportReport(path=export_path + '/' + proj_name + '_Report.pdf',
                       title=proj_name,
                       description="Processing Report: " + d3)

    # Export DEM
    if chunk.elevation:
        print("Exporting DEM")
        compression = Metashape.ImageCompression()
        compression.tiff_big = True
        chunk.exportRaster(path = export_path + '/' + proj_name + '_DEM.tif',
                           source_data = Metashape.ElevationData,
                           image_compression = compression,
                           north_up = True)
    else:
        print("No DEM Created, none exported")

    # Export Orthophotomosaic
    if chunk.orthomosaic:
        print("Exporting Orthophotomosaic")
        compression = Metashape.ImageCompression()
        compression.tiff_big = True
        chunk.exportRaster(path=export_path + '/' + proj_name + '_Ortho.tif',
                           source_data=Metashape.OrthomosaicData,
                           image_compression=compression,
                           save_kml=False,
                           save_world=False)
    else:
        print("No Orthophotomosaic Created, none exported")

    # Export Tiled Model
    # if chunk.tiled_model:
    #    chunk.exportTiledModel(export_path + '/' + proj_name + '_TiledModel.slpk',
    #                           source_data = Metashape.TiledModel)
    # else:
    #    print("No Tiled Model Created, none exported")

    # Close document to prevent error on next run
    Metashape.Document()

    # Define End Time
    end_time = time.time()
    print_time = time.ctime(end_time)
    print("End Time: ", print_time)
    delta_time = end_time - start_time
    delta_time_hours = datetime.timedelta(seconds=delta_time)
    converted_time = str(delta_time_hours)

    print("")
    print("Processing Report:")
    print("")
    print("Processing Competed In: ", converted_time)

    print('Processing finished, results saved to ' + export_path + '.')

print('Completed all sites in queue')