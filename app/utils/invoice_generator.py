from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os
from datetime import datetime

def generate_invoice_pdf(transaction, project, student):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='HeadingRight', parent=styles['Heading1'], alignment=2, fontSize=24, textColor=colors.HexColor('#4338ca')))
    styles.add(ParagraphStyle(name='SubHeading', parent=styles['Normal'], fontSize=12, textColor=colors.gray))
    styles.add(ParagraphStyle(name='FooterText', parent=styles['Normal'], fontSize=10, textColor=colors.gray, alignment=1))
    styles.add(ParagraphStyle(name='ReferralBonus', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#059669'), alignment=1, spaceBefore=6))
    
    # 1. Header Section (Logo Left, Title Right)
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img', 'logo.png')
    
    logo = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=0.6*inch)
        logo.hAlign = 'LEFT'
    
    header_data = [
        [logo, Paragraph("INVOICE", styles['HeadingRight'])],
        ["", Paragraph(f"#{transaction.invoice_ref or 'TRX-' + str(transaction.id)}", styles['Normal'])],
        ["", Paragraph(f"Date: {transaction.transaction_date.strftime('%b %d, %Y')}", styles['Normal'])]
    ]
    
    t_header = Table(header_data, colWidths=[3.5*inch, 3*inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 0.5 * inch))
    
    # 2. Company & Student Info
    company_info = [
        [Paragraph("<b>From:</b>", styles['Normal'])],
        [Paragraph("<b>Asan Innovators</b>", styles['Normal'])],
        [Paragraph("Hyderabad, Telangana, India", styles['Normal'])],
        [Paragraph("contact@asaninnovators.com", styles['Normal'])],
        [Paragraph("www.asandevnest.com", styles['Normal'])],
        [Paragraph("Ph: 86394990029, 7036222762, 9966645533", styles['Normal'])]
    ]
    
    student_info = [
        [Paragraph("<b>Bill To:</b>", styles['Normal'])],
        [Paragraph(f"<b>{student.student_name}</b>", styles['Normal'])],
        [Paragraph(student.phone, styles['Normal'])],
        [Paragraph(student.email or '', styles['Normal'])],
        [Paragraph(student.college or '', styles['Normal'])]
    ]
    
    info_data = [[Table(company_info), Table(student_info)]]
    t_info = Table(info_data, colWidths=[3.5*inch, 3*inch])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.3 * inch))
    
    # 3. Project Financial Summary
    payment = project.payments[0] if project.payments else None
    total_cost = payment.total_cost if payment else 0
    amount_paid = payment.amount_paid if payment else 0
    balance = payment.pending_balance if payment else 0
    
    summary_data = [
        ["Project", "Total Cost", "Total Paid", "Balance Due"],
        [Paragraph(project.title, styles['Normal']), f"₹ {total_cost:,.2f}", f"₹ {amount_paid:,.2f}", f"₹ {balance:,.2f}"]
    ]
    
    t_summary = Table(summary_data, colWidths=[3*inch, 1.2*inch, 1.2*inch, 1.1*inch])
    t_summary.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('padding', (0,0), (-1,-1), 6),
    ]))
    elements.append(Paragraph("<b>Project Summary</b>", styles['SubHeading']))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(t_summary)
    elements.append(Spacer(1, 0.3 * inch))

    # 4. Current Transaction
    elements.append(Paragraph("<b>Current Payment Details</b>", styles['SubHeading']))
    elements.append(Spacer(1, 0.1 * inch))
    
    item_data = [
        ["DESCRIPTION", "AMOUNT"],
        [f"Payment Ref: {transaction.invoice_ref or 'N/A'}", ""],
        [f"Mode: {transaction.payment_mode}", f"₹ {transaction.amount:,.2f}"],
        ["", ""],
        ["CURRENT PAID INFO", f"₹ {transaction.amount:,.2f}"]
    ]
    
    t_items = Table(item_data, colWidths=[4.5 * inch, 2 * inch])
    t_items.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#3730a3')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e7ff')), 
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), 
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 0.3 * inch))
    
    # 5. Payment History
    if payment and payment.transactions:
        elements.append(Paragraph("<b>Payment History</b>", styles['SubHeading']))
        elements.append(Spacer(1, 0.1 * inch))
        
        hist_data = [["Date", "Ref", "Mode", "Amount"]]
        for trx in sorted(payment.transactions, key=lambda x: x.transaction_date, reverse=True):
            hist_data.append([
                trx.transaction_date.strftime('%Y-%m-%d'),
                trx.invoice_ref or '-',
                trx.payment_mode,
                f"₹ {trx.amount:,.2f}"
            ])
            
        t_hist = Table(hist_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        t_hist.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (3,0), (3,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        elements.append(t_hist)
    
    # 6. Footer
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Thank you for choosing Asan Innovators!", styles['FooterText']))
    elements.append(Paragraph("<b>Refer & Earn:</b> Refer your friends and contact support to connect and get referral amount.", styles['ReferralBonus']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
