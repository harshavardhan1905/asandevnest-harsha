
@developer_bp.route('/project/<int:project_id>')
@login_required
@developer_required
def project_detail(project_id):
    """View project details"""
    project = Project.query.get_or_404(project_id)
    # Verify developer is member of the team assigned to this project
    is_member = False
    if project.team:
        for member in project.team.members:
            if member.developer_id == current_user.developer_profile.id:
                is_member = True
                break
    
    if not is_member:
        flash('Access denied. You are not a member of this project team.', 'danger')
        return redirect(url_for('developer.teams'))
        
    return render_template('developer/project_detail.html', project=project)
