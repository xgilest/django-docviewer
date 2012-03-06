import os
from subprocess import Popen, PIPE
from docviewer.settings import IMAGE_FORMAT
from docviewer.models import Document
from docviewer.tasks import generate_document

def docsplit(path):
    
    output = '/'.join(path.split('/')[:-1])
    
    commands = ["/usr/bin/docsplit images --size 700x,1000x,180x --format %s --output %s %s" % (IMAGE_FORMAT,output, path), 
                "/usr/bin/docsplit text --pages all --output %s %s" % (output, path)]
    
    for command in commands:
        result = Popen(command, shell=True, stderr=PIPE).stderr.read()
        
        if len(result) > 0:
            raise Exception(result)
        
    # rename directories
    os.rename("%s/%s" % (output, "1000x"), "%s/%s" % (output, "large"))
    os.rename("%s/%s" % (output, "700x"), "%s/%s" % (output, "normal"))
    os.rename("%s/%s" % (output, "180x"), "%s/%s" % (output, "small"))    
        
def create_document(filepath, doc_attributes):
    
    d = Document(**doc_attributes)
    d.save()
    
    filepath = d.set_file(filepath)
    
    
    task = generate_document.apply_async(args=[d.pk], kwargs={"filepath": filepath}, countdown=5)
    
    d.task_id = task.task_id
    d.save()
    
    return d