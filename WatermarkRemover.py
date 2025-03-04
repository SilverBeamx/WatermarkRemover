import os
import sys
import fitz

def backup_file(file_path):
    """Create a backup of the file in the 'backup' directory."""
    backup_dir = os.path.join(os.path.dirname(__file__), "backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    base_name = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, base_name)
    
    # If the backup file already exists, rename the new file
    if os.path.exists(backup_path):
        name, ext = os.path.splitext(base_name)
        counter = 1
        new_backup_path = os.path.join(backup_dir, f"{name}_{counter}{ext}")
        while os.path.exists(new_backup_path):
            counter += 1
            new_backup_path = os.path.join(backup_dir, f"{name}_{counter}{ext}")
        backup_path = new_backup_path
    
    with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
        dst.write(src.read())
    
    return backup_path

def process_page(page):
    """Process one page."""
    doc = page.parent  # the page's owning document
    page.clean_contents()  # clean page painting syntax
    xref = page.get_contents()[0]  # get xref of resulting /Contents
    changed = 0  # this will be returned
    # read sanitized contents, splitted by line
    cont_lines = page.read_contents().splitlines()
    for i in range(len(cont_lines)):  # iterate over the lines
        line = cont_lines[i]
        if not (line.startswith(b"/Artifact") and b"/Watermark" in line):
            continue  # this was not for us
        # line number i starts the definition, j ends it:
        j = cont_lines.index(b"EMC", i)
        for k in range(i, j):
            # look for image / xobject invocations in this line range
            do_line = cont_lines[k]
            if do_line.endswith(b"Do"):  # this invokes an image / xobject
                cont_lines[k] = b""  # remove / empty this line
                changed += 1
    if changed > 0:  # if we did anything, write back modified /Contents
        doc.update_stream(xref, b"\n".join(cont_lines))
    return changed


if __name__ == "__main__":

    for file_path in sys.argv[1:]:
        doc = fitz.open(file_path)
        changed = 0  # indicates successful removals
        for page in doc:
            changed += process_page(page)  # increase number of changes
        if changed > 0:
            # Get the last modified time of the file
            last_modified_time = os.path.getmtime(file_path)

            backup_file(file_path)
            x = "s" if doc.page_count > 1 else ""
            print(f"{changed} watermarks have been removed on {doc.page_count} page{x} in {os.path.basename(file_path)}")
            doc.ez_save(file_path.replace(".pdf", ".pdf.tmp"))
            doc.close()
            os.remove(file_path)
            os.rename(file_path + ".tmp", file_path)

            # Apply the last modified time to the new file
            os.utime(file_path, (last_modified_time, last_modified_time))
        else:
            print(f"Nothing to change in {os.path.basename(file_path)}")
    