import textwrap

sample_medline_xml = textwrap.dedent('''
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE MedlineCitationSet PUBLIC "-//NLM//DTD Medline Citation, 1st January, 2016//EN"
                                        "https://www.nlm.nih.gov/databases/dtd/nlmmedlinecitationset_160101.dtd">
    <MedlineCitationSet>
    <MedlineCitation Owner="NLM" Status="MEDLINE">
    <PMID Version="1">17687753</PMID>
    <DateCreated>
    <Year>2008</Year>
    <Month>03</Month>
    <Day>12</Day>
    </DateCreated>
    <DateCompleted>
    <Year>2008</Year>
    <Month>06</Month>
    <Day>05</Day>
    </DateCompleted>
    <DateRevised>
    <Year>2014</Year>
    <Month>07</Month>
    <Day>30</Day>
    </DateRevised>
    <Article PubModel="Print-Electronic">
    <Journal>
    <ISSN IssnType="Print">0300-8630</ISSN>
    <JournalIssue CitedMedium="Print">
    <Volume>220</Volume>
    <Issue>2</Issue>
    <PubDate>
    <MedlineDate>2008 Mar-Apr</MedlineDate>
    </PubDate>
    </JournalIssue>
    <Title>Klinische Pädiatrie</Title>
    <ISOAbbreviation>Klin Padiatr</ISOAbbreviation>
    </Journal>
    <ArticleTitle>[Low level auditory skills compared to writing skills in school children attending third and fourth grade: evidence for the rapid auditory processing deficit theory?].</ArticleTitle>
    <Pagination>
    <MedlinePgn>77-80</MedlinePgn>
    </Pagination>
    <Abstract>
    <AbstractText Label="BACKGROUND" NlmCategory="BACKGROUND">The rapid auditory processing defi-cit theory holds that impaired reading/writing skills are not caused exclusively by a cognitive deficit specific to representation and processing of speech sounds but arise due to sensory, mainly auditory, deficits. To further explore this theory we compared different measures of auditory low level skills to writing skills in school children.</AbstractText>
    <AbstractText Label="METHODS" NlmCategory="METHODS"/>
    <AbstractText Label="DESIGN" NlmCategory="METHODS">prospective study.</AbstractText>
    <AbstractText Label="SAMPLE" NlmCategory="METHODS">School children attending third and fourth grade.</AbstractText>
    <AbstractText Label="DEPENDENT VARIABLES" NlmCategory="METHODS">just noticeable differences for intensity and frequency (JNDI, JNDF), gap detection (GD) monaural and binaural temporal order judgement (TOJb and TOJm); grade in writing, language and mathematics.</AbstractText>
    <AbstractText Label="STATISTICS" NlmCategory="METHODS">correlation analysis.</AbstractText>
    <AbstractText Label="RESULTS" NlmCategory="RESULTS">No relevant correlation was found between any auditory low level processing variable and writing skills.</AbstractText>
    <AbstractText Label="DISCUSSION" NlmCategory="CONCLUSIONS">These data do not support the rapid auditory processing deficit theory.</AbstractText>
    </Abstract>
    <AuthorList CompleteYN="Y">
    <Author ValidYN="Y">
    <LastName>Ptok</LastName>
    <ForeName>M</ForeName>
    <Initials>M</Initials>
    <AffiliationInfo>
    <Affiliation>Klinik und Poliklinik für Phoniatrie und Pädaudiologie, Medizinische Hochschule Hannover. ptok.martin@mh-hannover.de</Affiliation>
    </AffiliationInfo>
    </Author>
    <Author ValidYN="Y">
    <LastName>Meisen</LastName>
    <ForeName>R</ForeName>
    <Initials>R</Initials>
    </Author>
    </AuthorList>
    <Language>ger</Language>
    <PublicationTypeList>
    <PublicationType UI="D003160">Comparative Study</PublicationType>
    <PublicationType UI="D004740">English Abstract</PublicationType>
    <PublicationType UI="D016428">Journal Article</PublicationType>
    </PublicationTypeList>
    <VernacularTitle>Basale auditorische Verarbeitung und Rechtschreibleistungen bei Schülerinnen und Schülern der 3. und 4. Jahrgangsstufe: Kann die "rapid auditory deficit"- These bestätigt werden?</VernacularTitle>
    <ArticleDate DateType="Electronic">
    <Year>2007</Year>
    <Month>08</Month>
    <Day>09</Day>
    </ArticleDate>
    </Article>
    <MedlineJournalInfo>
    <Country>Germany</Country>
    <MedlineTA>Klin Padiatr</MedlineTA>
    <NlmUniqueID>0326144</NlmUniqueID>
    <ISSNLinking>0300-8630</ISSNLinking>
    </MedlineJournalInfo>
    <CitationSubset>IM</CitationSubset>
    <MeshHeadingList>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D000367">Age Factors</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D000704">Analysis of Variance</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="Y" UI="D001307">Auditory Perception</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="Y" UI="D001308">Auditory Perceptual Disorders</DescriptorName>
    <QualifierName MajorTopicYN="N" UI="Q000175">diagnosis</QualifierName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D002648">Child</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="Y" UI="D004410">Dyslexia</DescriptorName>
    <QualifierName MajorTopicYN="N" UI="Q000175">diagnosis</QualifierName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D005260">Female</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D006801">Humans</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D008297">Male</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D011446">Prospective Studies</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D013223">Statistics as Topic</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="N" UI="D013998">Time Perception</DescriptorName>
    </MeshHeading>
    <MeshHeading>
    <DescriptorName MajorTopicYN="Y" UI="D014956">Writing</DescriptorName>
    </MeshHeading>
    </MeshHeadingList>
    </MedlineCitation>
    </MedlineCitationSet>
'''.strip('\n'))